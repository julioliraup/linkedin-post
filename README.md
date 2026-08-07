# linkedin-post

> **A GitHub Action to publish text or image posts to LinkedIn using the official Posts API.**

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-linkedin--post-blue?logo=github)](https://github.com/marketplace/actions/linkedin-post)
[![License](https://img.shields.io/github/license/julioliraup/linkedin-post)](LICENSE)

---

## Overview

This Composite Action wraps the LinkedIn [Images API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api) and [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api) so you can publish to LinkedIn in three lines of workflow YAML — with no heavy SDK required.

**Supported post types:**
- Text-only
- Text + single image (JPG, PNG, GIF)

---

## Prerequisites

### 1. LinkedIn Developer App

1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/) and create an app.
2. Under **Products**, request access to **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**.
3. Under **Auth**, generate an **Access Token** with the following OAuth 2.0 scopes:

| Scope | Purpose |
|---|---|
| `w_member_social` | Create posts on behalf of a member |
| `openid` + `profile` | Retrieve the member's `sub` (used to build the URN) |

> **Token expiry:** LinkedIn access tokens expire after **60 days**. Automate renewal using the [refresh token flow](https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens) or re-generate manually in the portal.

### 2. Find your Person URN

Call the OpenID userinfo endpoint with your token:

```bash
curl -H "Authorization: Bearer <TOKEN>" https://api.linkedin.com/v2/userinfo
```

The response contains a `sub` field. Your URN is `urn:li:person:<sub>`.

### 3. Add secrets to your repository

Go to **Settings → Secrets and variables → Actions** and create:

| Secret name | Value |
|---|---|
| `LINKEDIN_TOKEN` | Your OAuth access token |
| `LINKEDIN_URN` | `urn:li:person:<sub>` |

---

## Usage

### Text-only post

```yaml
- name: Post to LinkedIn
  uses: julioliraup/linkedin-post@v1
  with:
    linkedin_access_token: ${{ secrets.LINKEDIN_TOKEN }}
    linkedin_person_urn:   ${{ secrets.LINKEDIN_URN }}
    post_text: |
      New release is out!
      Check it out: https://github.com/julioliraup/my-project
```

### Post with an image

```yaml
- name: Post to LinkedIn
  uses: julioliraup/linkedin-post@v1
  with:
    linkedin_access_token: ${{ secrets.LINKEDIN_TOKEN }}
    linkedin_person_urn:   ${{ secrets.LINKEDIN_URN }}
    post_text:  'Check out our new banner! 🎨'
    image_path: 'assets/banner.png'
```

> `image_path` is relative to the repository root. The image must be checked out before this step runs (use `actions/checkout@v4`).

### Check the output

```yaml
- name: Post to LinkedIn
  id: linkedin
  uses: julioliraup/linkedin-post@v1
  with:
    linkedin_access_token: ${{ secrets.LINKEDIN_TOKEN }}
    linkedin_person_urn:   ${{ secrets.LINKEDIN_URN }}
    post_text: 'Automated post 🤖'

- name: Print result
  run: |
    echo "Status:  ${{ steps.linkedin.outputs.status }}"
    echo "Post ID: ${{ steps.linkedin.outputs.post_id }}"
```

---

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `linkedin_access_token` | ✅ | — | OAuth 2.0 access token |
| `linkedin_person_urn` | ✅ | — | Author URN (`urn:li:person:XXXXX`) |
| `post_text` | ❌ | `Posted automatically via GitHub Actions!` | Text body of the post |
| `image_path` | ❌ | `""` (no image) | Path to a local JPG, PNG or GIF file |
| `python_version` | ❌ | `3.11` | Python version used on the runner |

## Outputs

| Output | Description |
|---|---|
| `status` | `success` or `failure` |
| `post_id` | LinkedIn URN of the published post (e.g. `urn:li:share:...`) |

---

## Full workflow example — publish on every release

```yaml
name: Announce release on LinkedIn

on:
  release:
    types: [published]

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Post to LinkedIn
        uses: julioliraup/linkedin-post@v1
        with:
          linkedin_access_token: ${{ secrets.LINKEDIN_TOKEN }}
          linkedin_person_urn:   ${{ secrets.LINKEDIN_URN }}
          image_path: 'assets/release-banner.png'
          post_text: |
            🚀 ${{ github.event.release.name }} is out!

            ${{ github.event.release.body }}

            → ${{ github.event.release.html_url }}
```

---

## How it works

```
┌─────────────────────────────────────────────┐
│              GitHub Actions runner           │
│                                             │
│  1. actions/setup-python                    │
│  2. pip install requests                    │
│                                             │
│  3. share_linkedin.py                       │
│     ├── [if image_path set]                 │
│     │   ├── POST /rest/images               │
│     │   │   ?action=initializeUpload        │
│     │   │   → uploadUrl + image URN         │
│     │   └── PUT <uploadUrl> (binary)        │
│     └── POST /rest/posts                    │
│         ├── text-only  (no content key)     │
│         └── with image (content.media.id)   │
└─────────────────────────────────────────────┘
```

### API reference

| Step | Endpoint | Docs |
|---|---|---|
| Initialize image upload | `POST /rest/images?action=initializeUpload` | [Images API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api) |
| Upload image binary | `PUT <uploadUrl>` (returned by previous step) | [Images API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api) |
| Create post | `POST /rest/posts` | [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api) |

> **API version:** The action pins `LinkedIn-Version: 202504`. LinkedIn deprecates versions quarterly. Open an issue if a new version introduces breaking changes.

---

## Image requirements

- **Formats:** JPG, PNG, GIF (up to 250 frames for GIF)
- **Max pixels:** 36,152,320 px
- **Recommended dimensions:** 1200 × 627 px for optimal feed display

---

## License

[GPL-3.0](LICENSE) © [Julio Lira](https://julioliraup.github.io)
