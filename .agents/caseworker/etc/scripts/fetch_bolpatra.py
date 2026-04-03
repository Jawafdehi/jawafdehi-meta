"""
Fetch bolpatra (procurement documents) from bolpatra.gov.np

This script searches for procurement documents using an IFB/RFP/EOI/PQ number
and downloads all associated PDFs (bid documents, addendums, etc.)
"""

import requests
import re
import os
import sys
from bs4 import BeautifulSoup
import time
import urllib3

# Request timeout in seconds (connect, read)
DEFAULT_TIMEOUT = (10, 30)

# SSL verification is disabled by default for bolpatra.gov.np due to certificate issues
# The government website has a misconfigured certificate chain that prevents downloads
# Set ENFORCE_SSL_VERIFICATION=1 to enable strict certificate validation (will likely fail)
ENFORCE_SSL_VERIFICATION = os.environ.get('ENFORCE_SSL_VERIFICATION', '').lower() in ('1', 'true', 'yes')

if not ENFORCE_SSL_VERIFICATION:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("   WARNING: TLS certificate verification is disabled for bolpatra.gov.np", file=sys.stderr)
    print("   This is necessary due to the government website's SSL certificate issues.", file=sys.stderr)
    print("   Set ENFORCE_SSL_VERIFICATION=1 to enable (downloads will likely fail).\n", file=sys.stderr)

class BolpatraFetcher:
    BASE_URL = "https://www.bolpatra.gov.np/egp"
    
    def __init__(self, output_dir=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'{self.BASE_URL}/searchOpportunity',
            'X-Requested-With': 'XMLHttpRequest',
        })
        
        # Disable SSL verification by default due to bolpatra.gov.np certificate issues
        # Can be overridden with ENFORCE_SSL_VERIFICATION=1 environment variable
        if not ENFORCE_SSL_VERIFICATION:
            self.session.verify = False
        
        # Default output directory relative to script location
        if output_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "data", "bolpatra")
        
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _retry_request(self, func, *args, max_attempts=3, retryable_exceptions=(requests.exceptions.RequestException,), **kwargs):
        """
        Retry function with exponential backoff on transient failures.
        Retries timeouts and 5xx errors, but not 4xx or SSL errors.
        """
        backoff_delays = [1, 2, 4]
        
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            
            except requests.exceptions.HTTPError as e:
                # Use 'is not None' to avoid Response.__bool__ returning False for 4xx/5xx
                status = e.response.status_code if e.response is not None else None
                if status and status >= 500 and attempt < max_attempts - 1:
                    delay = backoff_delays[attempt]
                    print(f"  HTTP {status}, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                raise
            
            except retryable_exceptions as e:
                # Don't retry SSL errors (configuration issue)
                if isinstance(e, requests.exceptions.SSLError):
                    raise
                
                # Retry other transient errors
                if attempt < max_attempts - 1:
                    delay = backoff_delays[attempt]
                    print(f"  {type(e).__name__}, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                raise
    
    def _get_text(self, url, **kwargs):
        """GET URL and return text with automatic retry logic"""
        def _request():
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT, **kwargs)
            response.raise_for_status()
            return response.text
        return self._retry_request(_request)
    
    def search_by_ifb_number(self, ifb_number):
        """Search for tenders by IFB/RFP/EOI/PQ number"""
        print(f"Searching for IFB number: {ifb_number}")
        
        params = {
            'bidSearchTO.title': '',
            'bidSearchTO.ifbNO': ifb_number,
            'bidSearchTO.procurementCategory': '-1',
            'bidSearchTO.procurementMethod': '-1',
            'bidSearchTO.publicEntityTitle': '',
            'bidSearchTO.publicEntity': '0',
            'parentPE': '0',
            'null_widget': '',
            'bidSearchTO.childPEId': '-1',
            'bidSearchTO.NoticePubDateText': '',
            'bidSearchTO.lastBidSubmissionDateText': '',
            'bidSearchTO.contractType': '-1',
            'currentPageIndexInput': '1',
            'pageSizeInput': '10',
            'pageActionInput': 'first',
            'tenderId': '',
            'addNewJV': 'false',
            'currentPageIndex': '1',
            'pageSize': '10',
            'pageAction': '',
            'totalRecords': '1',
            'startIndex': '0',
            'numberOfPages': '1',
            'isNextAvailable': 'false',
            'isPreviousAvailable': 'false',
            'emergencyFlag': '0',
            '_': str(int(time.time() * 1000))
        }
        
        url = f"{self.BASE_URL}/SearchOpportunitiesResultHomePage"
        html = self._get_text(url, params=params)
        return self._parse_search_results(html)
    
    def _parse_search_results(self, html):
        """Parse search results to extract tender IDs and metadata"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        table = soup.find('table', {'id': 'dashBoardBidResult'})
        if not table:
            # Check for known empty-results marker
            no_records = soup.find(text=re.compile(r'no\s+records?\s+found', re.IGNORECASE))
            if no_records:
                print("No results found")
                return results
            # If table is missing and no empty-results marker, this is a parse failure
            raise ValueError("Search results table not found and no empty-results marker present - possible site change or error page")
        
        tbody = table.find('tbody')
        if not tbody:
            # Try to find rows directly if no tbody
            rows = table.find_all('tr', class_=re.compile(r'reltab'))
        else:
            rows = tbody.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 8:
                continue
            
            # Extract tender ID from onclick attribute
            link = cells[2].find('a')
            if link and 'onclick' in link.attrs:
                onclick = link['onclick']
                match = re.search(r"getTenderDetails\('(\d+)'\)", onclick)
                if match:
                    tender_id = match.group(1)
                    ifb_text = cells[1].get_text(strip=True).split('\n')[0].strip()
                    result = {
                        'tender_id': tender_id,
                        'ifb_number': ifb_text or 'Unknown',
                        'project_title': link.get_text(strip=True),
                        'public_entity': cells[3].get_text(strip=True),
                        'procurement_type': cells[4].get_text(strip=True),
                        'status': cells[5].get_text(strip=True),
                    }
                    results.append(result)
                    
                    # Log with smart truncation
                    title = result['project_title']
                    short_title = title[:60] + "..." if len(title) > 60 else title
                    print(f"Found: {short_title} (ID: {tender_id})")
        
        return results

    
    def get_tender_details(self, tender_id):
        """Get detailed information about a tender"""
        print(f"Fetching tender details for ID: {tender_id}")
        
        url = f"{self.BASE_URL}/getTenderDetails"
        params = {
            'tenderId': tender_id,
            '_': str(int(time.time() * 1000))
        }
        
        html = self._get_text(url, params=params)
        return self._parse_tender_details(html, tender_id)
    
    def _parse_tender_details(self, html, tender_id):
        """Parse tender details page to extract document download links"""
        soup = BeautifulSoup(html, 'html.parser')
        
        details = {
            'tender_id': tender_id,
            'documents': []
        }
        
        # Extract basic info by finding rows with IFB/RFP/EOI/PQ label
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                label_text = cells[0].get_text(strip=True)
                if 'IFB/RFP/EOI/PQ' in label_text:
                    details['ifb_number'] = cells[1].get_text(strip=True)
                elif 'Public Entity' in label_text or 'Organization' in label_text:
                    details['public_entity'] = cells[1].get_text(strip=True)
        
        # Find all download links
        download_links = soup.find_all('a', href=re.compile(r'download\?'))
        
        for link in download_links:
            href = link['href']
            # Extract alfId and docId from href
            match = re.search(r'alfId=([^&]+)&docId=(\d+)', href)
            if match:
                alf_id = match.group(1)
                doc_id = match.group(2)
                
                # Find document type and date from parent table
                row = link.find_parent('tr')
                if row:
                    cells = row.find_all('td')
                    doc_type = cells[0].get_text(strip=True) if len(cells) > 0 else 'Unknown'
                    pub_date = cells[1].get_text(strip=True) if len(cells) > 1 else 'Unknown'
                    
                    details['documents'].append({
                        'type': doc_type,
                        'publication_date': pub_date,
                        'alf_id': alf_id,
                        'doc_id': doc_id,
                        'download_url': f"{self.BASE_URL}/{href.lstrip('/')}"
                    })
        
        print(f"Found {len(details['documents'])} document(s)")
        return details
    
    def download_document(self, doc_info, tender_id, ifb_number):
        """
        Download and validate a document. Returns filepath or None on failure.
        Validates PDF magic bytes and cleans up partial files on error.
        """
        url = doc_info['download_url']
        
        # Sanitize filename components - replace any non-safe characters
        doc_type = re.sub(r'[^A-Za-z0-9._-]+', '_', doc_info['type'])
        pub_date = re.sub(r'[^A-Za-z0-9._-]+', '_', doc_info['publication_date'])
        doc_id = doc_info['doc_id']
        
        # Create filename with unique identifiers to prevent overwrites
        safe_ifb = re.sub(r'[^A-Za-z0-9._-]+', '-', ifb_number)
        safe_tender_id = re.sub(r'[^A-Za-z0-9._-]+', '-', str(tender_id))
        safe_doc_id = re.sub(r'[^A-Za-z0-9._-]+', '-', str(doc_id))
        filename = f"{safe_ifb}_{safe_tender_id}_{safe_doc_id}_{doc_type}_{pub_date}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        def _do_download():
            with self.session.get(url, stream=True, timeout=DEFAULT_TIMEOUT) as response:
                response.raise_for_status()
                
                # Validate content type
                content_type = response.headers.get('Content-Type', '').lower()
                if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                    print(f"  Warning: Unexpected Content-Type: {content_type}")
                
                # Download and validate PDF header
                first_chunk = None
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            if first_chunk is None:
                                first_chunk = chunk
                                # Validate PDF magic bytes
                                if not chunk.startswith(b'%PDF'):
                                    preview = repr(chunk[:20])
                                    raise ValueError(f"Downloaded file is not a valid PDF (starts with: {preview})")
                            f.write(chunk)
                
                if first_chunk is None:
                    raise ValueError("Downloaded file is empty")
                
                return filepath
        
        try:
            result_path = self._retry_request(
                _do_download,
                retryable_exceptions=(requests.exceptions.RequestException, ValueError)
            )
            print(f"  ✓ {doc_type}")
            return result_path
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"  Error downloading from {url}: {e}")
            # Clean up partial file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except OSError:
                pass
            return None
        except OSError as e:
            print(f"  File I/O error writing to {filepath}: {e}")
            # Clean up partial file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except OSError:
                pass
            return None
    
    def fetch_all_documents(self, ifb_number):
        """
        Search and download all documents for an IFB number.
        Returns dict with 'downloaded' (filepaths) and 'failed' (errors) lists.
        """
        print(f"\n{'='*60}")
        print(f"Fetching bolpatra documents for: {ifb_number}")
        print(f"{'='*60}\n")
        
        results = {
            'downloaded': [],
            'failed': []
        }
        
        # Search for the tender
        try:
            search_results = self.search_by_ifb_number(ifb_number)
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Error searching for tender: {e}")
            results['failed'].append({'stage': 'search', 'error': str(e)})
            return results
        except Exception as e:
            print(f"Unexpected error searching for tender: {e}")
            results['failed'].append({'stage': 'search', 'error': f"Unexpected: {e!s}"})
            return results
        
        if not search_results:
            print("No tenders found")
            return results
        
        # Process each result
        for result in search_results:
            tender_id = result['tender_id']
            print(f"\nProcessing tender ID: {tender_id}")
            
            # Get tender details
            try:
                details = self.get_tender_details(tender_id)
            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"Error fetching tender details: {e}")
                results['failed'].append({
                    'stage': 'details',
                    'tender_id': tender_id,
                    'error': str(e)
                })
                continue
            except Exception as e:
                print(f"Unexpected error fetching tender details: {e}")
                results['failed'].append({
                    'stage': 'details',
                    'tender_id': tender_id,
                    'error': f"Unexpected: {e!s}"
                })
                continue
            
            # Download all documents
            if details['documents']:
                print(f"Downloading {len(details['documents'])} document(s)...")
            for doc in details['documents']:
                filepath = self.download_document(doc, tender_id, result['ifb_number'])
                if filepath:
                    results['downloaded'].append(filepath)
                else:
                    results['failed'].append({
                        'stage': 'download',
                        'tender_id': tender_id,
                        'doc_type': doc.get('type', 'Unknown'),
                        'url': doc.get('download_url', 'Unknown')
                    })
        
        print(f"\n{'='*60}")
        if results['downloaded']:
            print(f"Downloaded {len(results['downloaded'])} document(s) to: {self.output_dir}")
        if results['failed']:
            print(f"Failed: {len(results['failed'])} operation(s)")
        print(f"{'='*60}\n")
        
        return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_bolpatra.py <IFB_NUMBER>")
        print("Example: python fetch_bolpatra.py 'Re-PPHL2/G/NCB/02/2079-80'")
        sys.exit(1)
    
    ifb_number = sys.argv[1]
    
    fetcher = BolpatraFetcher()
    results = fetcher.fetch_all_documents(ifb_number)
    
    # Exit with appropriate code
    if not results['downloaded']:
        print("No files downloaded", file=sys.stderr)
        sys.exit(1)
    elif results['failed']:
        print(f"Downloaded {len(results['downloaded'])} file(s), but {len(results['failed'])} operation(s) failed", file=sys.stderr)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
