# MorningBot Contribution Guidelines

## General PR Guidelines
- PRs need a title that gives maintainers an idea of the changes being made at a first glance
- Descriptions should explain what the pr is doing, why it's needed and how it's being done. Your PR won't be looked at if these criteria aren't met.
- Blast Radius: Each PR should address one problem only, if you want to do a full rewrite then fork it and do it on your own repo. Anything which spans multiple files must have a good reason behind it.
- Test coverage, if you are adding a feature, please include the proper test/CI if github actions is configured.

### Introductory/Minor PRs
- Docs.
- Changing config files.
- Simple fixes/improvements to code (1-5 lines).

### Medium PRs
- Fixing larger bugs.
- Implementing minor features.
- Configuring CI.

### Major PRs
- Implementing Planned features.
- Implementing CI/CD pipelines.
- Changing structure of repo.
- Rewriting large chunks of code to address some problems.
