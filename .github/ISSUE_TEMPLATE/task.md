---
name: Task
about: Not intended for users! 
title: Summary
labels: task
assignees: iBrotNano
---

## :dart: Requirements

### :spiral_notepad: Description

What has to be done?

### :question: Open Questions?
1. @Who: What must be discussed?

### :construction: Blockers

1. Something blocks my work.

### :control_knobs: Conditions
What conditions must be met? High pressure? Many users?

### :warning: Side effects

Are there any?

## :heavy_check_mark: Acceptance tests
- [ ] Test to validate the requirement.

## :triangular_ruler: Design

How can the task be done?

## :microscope: Dissection
| Integration test | ID                                          |
| ---------------- | ------------------------------------------- |
| Action           | What has to be done to validate the system? |
| Expected result  | What is a valid result?                     |

## :hammer_and_wrench: Development

### :clipboard: TODOs

- [ ] Create a `feature` branch if needed (Maybe configuration changes or new project files)
- [ ] Update the dependencies
- [ ] Document the updated dependencies in CHANGELOG.md
- [ ] Here is the place for development todo items
- [ ] Check if the exception handling is well done
- [ ] Check if further tests must be written
- [ ] Are there license conflicts for new dependencies?
- [ ] Exisits a `global.json`
- [ ] Are all TODOs in the code done?
- [ ] Write meaningful comments
- [ ] Are there any compiler warnings?
- [ ] Do all unit tests pass in Visual Studio?
- [ ] Do all unit tests pass with `dotnet test`?
- [ ] `dotnet format Contracts.Service.sln --verify-no-changes --verbosity diagnostic`
- [ ] Is the version number correctly configured?
- [ ] Phrase a meaningful commit comment
- [ ] Check-in the changes and push them to the server
- [ ] Does the build on the buildserver succeed?
- [ ] Create a PR

### :eyes: Review

- [ ] Initialize dev environment
- [ ] Checkout the version from Git
- [ ] Can the application be compiled?
- [ ] Are there any open warnings?
- [ ] Does the application work as a manually performed test?
- [ ] Is the layout and theme working in the UI?
- [ ] Is the UI translated?
- [ ] Is every input validated in frontend and backend?
- [ ] Are the requirements and acceptance criteria met?
- [ ] Is the code correct, clean, maintainable and well structured?
- [ ] Is the code well tested?
  - [ ] Does the test name describe the context and goal from a business perspective? What is being specified, not how it is technically implemented.
  - [ ] One aspect per test?
  - [ ] One essential assert per test. Asserts for the context should be marked as such.
  - [ ] Side-effect free and complete? No shared **instances** of objects. Especially the SUT.
  - [ ] Only fixed input data?
  - [ ] Only own code is tested?
  - [ ] Does each component have a test suite?
- [ ] Must something in README.md be updated or described?
- [ ] Does the pipeline work?
- [ ] Are there new database migrations before merging to `main`? This ensures that the database will be in the correct state after deployment.
- [ ] Shut down the dev environment

### :memo: Notes

Notes about the development of the issue.

> [!NOTE]
> This is a note

> [!TIP]
> This is a tip.

> [!WARNING]
> This is a warning

> [!IMPORTANT]
> This info is important to know.

> [!CAUTION]
> This has possibly negative consequences.

## :mag: Debug

- [ ] ID: 🟢🔴🟡 Result: As Expected

## :books: Documentation
- [ ] Do I need a new PIA or update an existing one?
- [ ] Update the README.md
- [ ] Update the CHANGELOG.md
- [ ] Describe the setup of the story if needed for end users
- [ ] Does something in the wiki needed to be updated?
- [ ] Needs other stuff been documented?

### :bulb: Decisions

| Decision          | Cause                      |
| ----------------- | -------------------------- |
| What was decided? | Why was the decision made? |

### :page_facing_up: PIAs

Link to related PIA

### :link: Links
- Any other documentation should be linked here. Intern and extern.

## :clapper: Demo

- [ ] Setup a fresh demo environment
- [ ] Check all acceptance tests

## :package: Deployment

- [ ] Merge `feature` into `master` or `hotfix` into `production` and `master` and remove the `bugfix` branch
- [ ] Check if the compiled artifact is valid
- [ ] Cleanup the Git history locally on the dev system

## :beer: Retro

> [!TIP]  Was gab es zu lernen?
> What did I learn?

> [!WARNING] Where were the problems?
> Where did I have difficulties? What hindered my work?

## :unicorn: Magie

Hints and tricks that were helpful during the implementation or documentation.

<details>
    <summary>Emojis to label information</summary>

| Emoji                | Bedeutung                 |
| :------------------- | :------------------------ |
| :x:                  | Nein                      |
| :ok:                 | Ja                        |
| :warning:            | Achtung                   |
| :information_source: | Zusätzliche Informationen |
| :zzz:                | Wartet                    |
| :red_circle:         | Fehlschlag                |
| :green_circle:       | Erfolg                    |
| :yellow_circle:      | Problem                   |
</details>

<details> 
    <summary>PR</summary>

A PR needs a title that lets the reviewer recognize which ticket it belongs to. The format is:

`#<issue number> <issue title>`

It helps the reviewer if you provide details about the development environment. Breaking changes in services can make it unclear which versions of services the reviewer should use for the review.

The versions can be set up from artefacts or via Git by using the correct branches.

If the exact version is not critical, it may be sufficient to simply use the image with latest.

Here is a template for a PR:

```markdown
## Notes

BREAKING CHANGE: Is this a breaking change?

Is there anything special to note? Perhaps deviations from the ticket or details that came up during development?

## Changes

- Fixed a typo
- Optimized code
- New feature XYZ

## Development environment

### Versions

| Application | Version |
| :---------- | ------: |
| Client      |   1.5.0 |
| Service     |   1.2.4 |
| KeyCloak    |  latest |
| Postgres    |  latest |

### Setup

Scripts or test data used? Ideally attach or link it.
```
</details>

<details>
    <summary>Database migration with EF Core</summary>

```powershell
PS> cd .\src\ProjectName
PS> dotnet ef database update
PS> dotnet ef migrations add <migration_name> --project ..\ProjectName.csproj
```

`dotnet ef` can be updated with the command `dotnet tool update -g dotnet-ef --version 7.0.14`.

During development, sometimes it is necessary to recreate a migration:

```powershell
# List all migrations an copy the one to reset the database to.
dotnet ef migrations list

dotnet ef database update <migration_name> && dotnet ef migrations remove && dotnet ef migrations add <migration_name> --project ..\ProjectName.csproj && dotnet ef database update
```

> [!WARNING] ATTENTION
> Before merging into `main`, you must check if there are new migrations. The best way to do this is by comparing the migrations in `main` with those in your own branch. It is a good idea to commit migrations separately so that they can be easily reverted if necessary.

If there are new migrations on `main`, proceed as follows:

1. With the feature branch, reset the database to the last state before your own migration. `dotnet ef database update <migration_name>`
2. On the feature branch, remove the last commit with a `reset`.
3. Merge `main`.
4. Now create a new migration. `dotnet ef migrations add <migration_name> --project ..\ProjectName.csproj && dotnet ef database update`
5. Commit the migration.
</details>