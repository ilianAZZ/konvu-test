# Konvu technical test

## Steps

1. Run `pip install -r requirements.txt` to install dependencies.
2. Set your constants in `./src/env.py`. (actual env file contains a ready-to-use agent with few files in context)
3. Run `cd ./src && python main.py <osv_vuln_id> <project_path>` to execute the CVE explanation process.

## Description

This project is composed in two main parts:

1. **Agent initialization**: The agent is initialized with a document library containing code files from a specified codebase. The agent is created once and can be reused for multiple CVE analyses. ATM the agent name is in a constant in env.py. But it can be easily modified to be dynamic and handle multiple projects.

   - 1. Create a library (Mistral API)
   - 2. Parse git project to extract code files (using the git project, following the .gitignore rules)
   - 3. Upload files content & names to the library using (Mistral API)
   - 4. Create an agent with the library in context (Mistral API)

2. **CVE explanation**: For each CVE, the script fetches CVE data (OSV dev API), generate a prompt and uses Mistral API to get an explanation of how the CVE affects the codebase, by prompting the agent created in step 1.

The API/web server can be started running :

```bash
python api.py
```

But this feature (html & flask server) was fully AI generated only for fun. It seems to be working but was not fully tested.

## Limitations

The Mistral AI freetier is limited to 10 files in the document library. So the output will be very very limited. To fully test the agent capabilities, different options are listed in the conclusion.

## Proof of concept

The code was tested on a large codebase with a monorepo structure. Due to the limit of 10 files, only few config files were added (.dockerignore, prettier, docker deploy files, gitignore, etc.)

Using Mistral API, we can retreive the list of files in the document library.

```text
🧠  Agent Document Library Context
====================================

📚  Agent uses 1 document library:

🗂️  Library ID: 019a2a80-8c0d-7532-a60f-05f067336075
   🔸 Name: VulnCodeAnalyzer_LIB
   📝 Description: Library for konvu code analysis

   📄 Documents:
   ────────────────────────────────────────────────────────────
   🧾 Name                             📏 Size
   ────────────────────────────────────────────────────────────
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.vscode/settings.json        2104 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.prettierrc          323 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.prettierignore      440 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.gitignore           125 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.github/workflows/playwright.yml     678 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.github/workflows/deploy.yml         7857 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.github/workflows/_discord_notif.yml         3128 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.github/dependabot.yml       525 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.gitattributes       18 bytes
   /Users/ilian/Documents/HeadOfScience/HOS-V2/.dockerignore        1419 bytes
   ────────────────────────────────────────────────────────────
```

When prompting the agent to list all files, we successfully got a summary of those files :

```text
Generated Prompt:
As an agent, explore all FILES un the document library of you context, Analyse all files and make a report of main feature of the codebase based on the dependencies and code. AND LIST OF THE FILES INTHE CONTEXT LIBRARY
------
Based on the search results, here is a list of files found in the document library:

1. **.gitignore**: This file specifies intentionally untracked files that Git should ignore. It includes build artifacts, configuration files, environment files, and tool-specific configurations for Turbo, Vite, and VSCode.

2. **.dockerignore**: This file lists files and directories to be excluded or ignored when building Docker images. It includes dependencies, caches, build artifacts, tests, documentation, development configurations, environment variables, and Git-related files.

3. **.prettierignore**: This file lists patterns for files and directories that Prettier (a code formatter) should ignore. It includes global directories like `node_modules` and `dist`, app-specific directories, and various log and cache files.

4. **.gitattributes**: This file specifies attributes for paths in a Git repository, such as setting the end-of-line character to a line feed (lf) and handling text files automatically.

These files are typically used to manage and configure different aspects of a software development project, ensuring that unnecessary files are ignored by various tools and processes.
```

We can try to ask the agent to list all files ignored by git, to make sure the content of files is properly ingested, and not only the file names.

```text
Generated Prompt:
As an agent, explore the gitignore files in the document library and list all files ignored by git.
------
The `.gitignore` files in the document library list various files and directories that are to be ignored by Git. Here are the files and directories that are ignored:

1. **Dependencies and Caches:**
   - `**/node_modules`
   - `**/.pnpm-store`
   - `**/.npm`
   - `**/.yarn`
   - `**/.turbo`
   - `**/*cache*`
   - `**/.jest-cache`
   - `**/.nyc_output`

[...]

14. **API Files:**
    - `apps/api/src/google-api-iazz-manager.json`
    - `apps/api/src/oauth-google-api-iazz-manager.json`
```

This confirms that the agent is able to read and understand the content of the document library.
Specifically the two last files that are very specific to this codebase.

### Test with a docker vulnerability

For this test, docker is present, but there is not enough context to have a meaningful output.

In that case, the output should be uncertain or not enough information.

```text
### Vulnerability Analysis Report

#### 1. What is this vulnerability?
The vulnerability CVE-2024-21626 involves a container breakout issue in runc, a tool for spawning and running containers on Linux. Due to an internal file descriptor leak, an attacker could manipulate the working directory of a newly spawned container process, allowing access to the host filesystem. This could lead to a container escape, giving unauthorized access to the host system.

#### 2. Is this codebase affected?
**Uncertain**

The codebase uses Docker for building and deploying containerized applications, as indicated by the presence of Dockerfiles and Docker Compose files. However, there is no explicit evidence in the provided documents that directly indicates the use of runc or its version. The vulnerability affects runc versions 1.1.11 and earlier, but without specific version information or explicit usage of runc in the codebase, it's uncertain if the codebase is affected.

#### 3. Risk Assessment
If the codebase is using an affected version of runc, the risk is high as it could allow attackers to escape container boundaries and access the host filesystem. However, since the usage and version of runc are not explicitly stated, the risk cannot be definitively assessed.

#### 4. Recommended Actions
- **Verification Steps:**
  - Verify if runc is used in the codebase and check its version.
  - Review Docker configurations and deployment scripts to ensure no vulnerable versions of runc are being utilized.

- **Preventive Measures:**
  - Ensure that all container-related tools and dependencies are updated to their latest secure versions.
  - Regularly audit and update container management tools and dependencies.

#### 5. Production Impact
The dependency/tool in question (runc) would be used at runtime if it is part of the container deployment process.

#### 6. Confidence Level
**Low**

The confidence level is low due to the lack of explicit information regarding the use and version of runc in the codebase.

#### 7. Is risky for the project?
**Uncertain**

The risk to the project is uncertain due to insufficient evidence regarding the use of runc. Further investigation is required to determine if the project is at risk.
```

This shows that the agent is able to provide a structured analysis of the CVE based on the limited context it has. The agent output (uncertain, low confidence) is appropriate given the lack of specific information about runc in the codebase.

In a real scenario, having more files in context (like package.json, docker-compose.yml, deployment scripts, etc.) would help the agent to provide a more accurate analysis.


## Conclusion

This technical test seems to be working as expected. The agent is able to ingest code files from a codebase and provide explanations of CVEs based on that context.

It could be improved by :

- Preprocess the codebase to create a context of the project (dependencies, main features, architecture, OS runtime, frameworks used, etc.) to provide more meaningful context to the agent.
- Remove the 10 file limit :
  - Use another agent provider,
  - Pay for a higher tier on Mistral,
  - Try to implement this solution without library, just by providing files as tools (not tested yet, may be limited as well).
- Improve the prompt engineering for better results.
- Handle multiple projects/agents (for example, by using a hash of the codebase path as agent name).
- For a normal project, the .env file should be excluded from git and not shared publicly, and not as a python file with constants.
- Add proper error handling and logging for production use and debugging. Also to be able to have statistics on failures/success rate.
- Add unit test with mocks of OSV APIs, to make sure the code is working as expected. For example we can create a new CVE issue "any code with a function named test is vulnerable" and test that the agent is able to identify that in a codebase with a function named test.
- Parse the LLM Output to have a structured JSON response instead of plain text, and be able to "tag" the CVE as risky or not based on the analysis.
- Remove the absolute path in the document library files names, to avoid potential leaking sensitive information. But in the other hand, having the full path may help the agent to better understand the project structure and have more context.
- Better file architecture and separation of concerns for production use.
