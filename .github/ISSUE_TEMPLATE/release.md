---
name: Release
about: Not intended for users! 
title: Release vx.x.x
labels: ''
assignees: iBrotNano

---

## :mag: Details

| Name      | Value                     |
| :-------- | :------------------------ |
| Milestone | [1.0.0](Url to Milestone) |
| Owner     | @owner                    |

### :clipboard: Todo

- [ ] Create a `release` branch from `master` for the RC
- [ ] Start the test phase
- [ ] Collect all test results
- [ ] Create bugfix issues if needed for the current release
- [ ] Start bugfixing
- [ ] Redo the test phase
- [ ] Update the version number for the release (Major.Minor.Patch)
- [ ] Are there license conflicts for dependencies?
- [ ] Merge `release`  into `master` and `production` with `fast forward`
- [ ] Tag `production` with version number from current milestone
- [ ] Update the Changelog in the wiki
- [ ] Complete the release page of the current release in the wiki
- [ ] Move old release page into the archive folder
- [ ] Close the milestone
- [ ] Backup all project files for documentation
- [ ] Release the application into production

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

Nothing to mention.

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