# Sweet Spot File Sizing (<300 Lines) & Single Responsibility

- **Target and Ceiling**:
  - Target: Keep Python files within **50–200 lines**.
  - Hard Ceiling: **300 lines maximum** per file.
- **Decomposition Guidelines**:
  - Handlers (`handlers/`): Command/callback routing and user feedback. When logic grows, delegate into `core/runner.py` or separate services.
  - UI Keyboards (`ui/`): Pure inline keyboard markup builders without state mutation.
  - Core (`core/`): Environment configuration, health servers, and host executionFacades.
  - Constants (`constants/`): Clean metadata, country profiles, and emoji maps.
- **Automated Enforcement**: All files must pass `analyze.sh` Sweet Spot gate.
