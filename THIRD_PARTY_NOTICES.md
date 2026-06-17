Status: AUTHORITATIVE LEGAL NOTICE INDEX
Last Reviewed: 2026-06-17
Supersedes: none
Superseded By: none
Stability: controlled
Future Series: LEGAL
Applies To: third-party code, dependencies, assets, data, tools, documentation, fonts, models, generated output, and other third-party material used by Dominium or Domino

# DOMINIUM THIRD-PARTY NOTICES
## Version 1.0

This file is the public index for third-party material used by Dominium and Domino.

`LICENSE.md` governs project-owned material. Third-party material remains governed by its own license terms.

---

# 1. BASIC RULE

Dominium must not claim ownership or unrestricted control over material owned by third parties.

If a file, dependency, asset, tool, model, dataset, font, generated output, package, or other component is owned by a third party, the relevant third-party license and notice obligations continue to apply to that component.

Nothing in `LICENSE.md`, `CONTRIBUTOR_LICENSE_AGREEMENT.md`, `TRADEMARKS.md`, or other project terms grants more rights in third-party material than the relevant third-party owner grants.

---

# 2. CURRENT NOTICE STATUS

This notice index is established as a legal control surface.

Known third-party notices should be added here or in scoped notice files before release, distribution, commercial licensing, public binary publication, or broader packaging.

At this time, this file does not certify that all third-party material has been audited. It records the required location for notices and the rules for adding them.

---

# 3. REQUIRED NOTICE ENTRIES

When third-party material is added or identified, record at least:

| Field | Required meaning |
|---|---|
| Component | Name of the third-party component or material. |
| Location | Repository path, package reference, dependency name, or source location. |
| Owner / Author | Copyright owner or upstream project where known. |
| License | License name and version where known. |
| Source | Upstream URL, package registry, vendor source, or provenance reference where appropriate. |
| Use | How Dominium uses the material. |
| Notice obligations | Attribution, copy of license, source offer, modification notice, patent notice, or other obligations. |
| Review status | Pending, reviewed, approved, replaced, quarantined, or removed. |

---

# 4. CONTRIBUTION RULE

Do not contribute third-party material unless it is clearly identified and legally compatible with the Project Owner's intended restricted-source and potential commercial licensing model.

Contribution submissions involving third-party material must comply with `CONTRIBUTOR_LICENSE_AGREEMENT.md` and must identify provenance, license, and compatibility.

The Project Owner may reject, remove, quarantine, or rewrite material that lacks adequate provenance or has incompatible terms.

---

# 5. PROHIBITED MATERIAL WITHOUT REVIEW

Do not add the following without explicit review:

1. copyleft code or assets that may require relicensing project-owned material;
2. code copied from tutorials, answers, snippets, repositories, gists, forums, generated examples, or AI outputs without provenance;
3. fonts, icons, sounds, images, textures, models, music, maps, datasets, or other assets without license evidence;
4. proprietary SDKs, restricted APIs, commercial assets, leaked material, credentials, private datasets, or access-controlled content;
5. material with non-commercial-only, no-derivatives, field-of-use, attribution-chain, patent-retaliation, network-use, source-availability, or redistribution obligations that conflict with project licensing;
6. content whose author, owner, or legal origin is unclear.

---

# 6. NOTICE ENTRY TEMPLATE

Use this template when adding an entry:

```md
## [Component Name]

| Field | Value |
|---|---|
| Component |  |
| Location |  |
| Owner / Author |  |
| License |  |
| Source |  |
| Use |  |
| Notice obligations |  |
| Review status | Pending |
```

---

# 7. RELEASE RULE

Before any public binary release, commercial licensing event, public package, installer, hosted service, SDK, demo, preview, or broader distribution, third-party material must be reviewed and this notice index or scoped notice files must be updated.

A green build, passing test suite, or accepted pull request does not by itself certify third-party license compliance.

---

# 8. CONTACT

Questions about third-party material, provenance, dependency licensing, notices, replacements, or removals should be directed through the Official Repository or another contact channel formally published by the Project Owner.
