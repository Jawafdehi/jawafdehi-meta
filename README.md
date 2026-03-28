# Jawafdehi.org Meta-Repository

Jawafdehi.org is a civic tech organization building open digital infrastructure to empower Nepali citizens with transparent access to information about governance, corruption, and public entities.

This meta-repository serves as the central hub for the entire Jawafdehi.org ecosystem, consolidating all projects, services, infrastructure code, documentation, and research materials in one place.

**Repository**: https://github.com/Jawafdehi/jawafdehi-meta

By centralizing documentation and specifications across multiple services, the meta-repo provides a single source of truth that streamlines agentic development and AI-assisted coding workflows. This architecture enables efficient collaboration, consistent standards, and seamless integration across all Jawafdehi.org platforms.

## Jawafdehi.org Projects

Jawafdehi.org consists of four major projects, each with their own subcomponents:

1. **Jawafdehi.org** - Open database of corruption and accountability
   - **Live Platform**: https://jawafdehi.org
   - Services: `jawafdehi-api`, `jawafdehi-frontend`

2. **NES (Nepal Entity Service)** - Comprehensive database of Nepali public entities (persons, organizations)
   - Services: `nes`, `nes-tundikhel`, `nes-assets`

3. **NGM (Nepal Governance Modernization)** - Judicial data collection and governance analysis
   - Services: `ngm`

All platforms emphasize open source code, open data principles, bilingual support (English/Nepali), and complete audit trails to promote transparency and accountability in Nepali governance.

## Who Should Use This Meta Repo?

### Team Members & Interns
If you're a **Jawafdehi.org team member** or **intern**, this meta-repository is designed for you. It provides:
- Complete context for all services and their relationships
- Shared documentation, research materials, and tooling
- AI-enriched context for GenAI tools (Cursor, Kiro, GitHub Copilot, etc.)
- Cross-service coordination and infrastructure management

**👉 [Start Here: Getting Started Guide](docs/GETTING_STARTED.md)**

### Open Source Contributors
If you're an **open source contributor**, you can work directly with individual service repositories without needing the meta repo.

**👉 [Learn More: Contributor Workflows](docs/CONTRIBUTOR_WORKFLOWS.md)**

**Primary open source target**: [Nepal Entity Service (NES)](https://github.com/Jawafdehi/nes)

## Available Services

Services are independent repositories that you can clone selectively - you only need to clone what you're working on. See the [Getting Started Guide](docs/GETTING_STARTED.md) for setup instructions.

| Service | Description | Repository | Clone Command |
|---------|-------------|------------|---------------|
| **jawafdehi-api** | Django accountability API | [Jawafdehi/JawafdehiAPI](https://github.com/Jawafdehi/JawafdehiAPI) | `git clone git@github.com:Jawafdehi/JawafdehiAPI.git jawafdehi-api` |
| **jawafdehi-frontend** | React public frontend | [Jawafdehi/Jawafdehi](https://github.com/Jawafdehi/Jawafdehi) | `git clone git@github.com:Jawafdehi/Jawafdehi.git jawafdehi-frontend` |
| **nes** | Nepal Entity Service database | [Jawafdehi/NepalEntityService](https://github.com/Jawafdehi/NepalEntityService) | `git clone git@github.com:Jawafdehi/NepalEntityService.git nes` |
| **nes-tundikhel** | NES explorer UI | [Jawafdehi/NepalEntityService-tundikhel](https://github.com/Jawafdehi/NepalEntityService-tundikhel) | `git clone git@github.com:Jawafdehi/NepalEntityService-tundikhel.git nes-tundikhel` |
| **nes-assets** | NES static assets site | [Jawafdehi/NepalEntityService-assets](https://github.com/Jawafdehi/NepalEntityService-assets) | `git clone git@github.com:Jawafdehi/NepalEntityService-assets.git nes-assets` |
| **ngm** | Nepal Governance Modernization | [Jawafdehi/ngm](https://github.com/Jawafdehi/ngm) | `git clone git@github.com:Jawafdehi/ngm.git ngm` |
| **infra** | Infrastructure as Code (Terraform) | [Jawafdehi/GCP-deployment](https://github.com/Jawafdehi/GCP-deployment) | `git clone git@github.com:Jawafdehi/GCP-deployment.git infra` |

## Repository Structure

```
/
├── .kiro/                  # Kiro IDE configuration (meta-repo level)
│   ├── specs/              # Feature specifications (shared)
│   └── steering/           # AI steering rules (shared)
├── .amazonq/               # Amazon Q configuration
│   └── rules/              # Amazon Q rules
├── .cursor/                # Cursor IDE configuration
│   └── rules/              # Cursor rules
├── .github/                # GitHub configuration (workflows, templates)
│
├── services/               # All application services (independent repositories)
│   ├── jawafdehi-api/      # Django accountability API
│   ├── jawafdehi-frontend/ # React public frontend
│   ├── nes/                # Nepal entity database
│   ├── nes-tundikhel/      # NES explorer UI
│   ├── nes-assets/         # NES static assets
│   └── infra/              # Infrastructure as Code (independent repository)
│       ├── terraform/      # Terraform configuration
│       └── misc/           # Build configs and scripts
│
├── docs/                   # Meta-repo documentation (cross-cutting concerns)
├── case-research/          # Case research materials
├── laboratory/             # Experimental code and toolkits
└── tools/                  # Shared development tools

Note: Services are independent repositories. Clone them into the services/ directory as needed.
For full details on repository setup and selective cloning, see docs/GETTING_STARTED.md.
Each service also has its own docs/ folder for service-specific documentation.
```

## Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Setup instructions for team members and contributors
- **[Contributor Workflows](docs/CONTRIBUTOR_WORKFLOWS.md)** - Understand team vs open source workflows
- **[Project Board](https://app.asana.com/1/1212011274276450/home)** - Current tasks and priorities

## Technology Stack

- **Backend**: Python 3.12+, Django 5.2+, Poetry
- **Frontend**: TypeScript, React 18, Vite, Bun
- **Database**: PostgreSQL
- **Infrastructure**: Google Cloud Platform, Terraform

## Contributing

See our [Contributor Workflows](docs/CONTRIBUTOR_WORKFLOWS.md) guide to understand the best way to contribute based on your role.

## License

MIT
