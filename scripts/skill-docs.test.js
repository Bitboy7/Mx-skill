// allow: SIZE_OK - Repository-wide documentation invariants remain one catalog-oriented suite.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const childProcess = require("node:child_process");

const repoRoot = path.join(__dirname, "..");

function read(relativePath) {
  // CLI-managed skills keep their authored content in skill.json (frontmatter)
  // + instruction.md; the committed SKILL.md is a generated CLI stub. Content
  // tests keep asserting against the logical document.
  const skillMatch = relativePath.match(/^([a-z0-9-]+)[\\/]SKILL\.md$/);
  if (skillMatch) {
    const manifestPath = path.join(repoRoot, skillMatch[1], "skill.json");
    if (fs.existsSync(manifestPath)) {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
      const instruction = fs.readFileSync(path.join(repoRoot, skillMatch[1], "instruction.md"), "utf8");
      return `---\n${manifest.frontmatter.trim()}\n---\n\n${instruction}`;
    }
  }

  return fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
}

function readRaw(relativePath) {
  return fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
}

function readJson(relativePath) {
  return JSON.parse(read(relativePath));
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function findSection(doc, heading) {
  const escaped = escapeRegex(heading);
  const match = doc.match(new RegExp(`${escaped}[\\s\\S]*?(?=\\n## |\\n### |$)`));

  assert.ok(match, `expected section headed by "${heading}"`);
  return match[0];
}

function trackedTextFiles() {
  return childProcess
    .execFileSync("git", ["ls-files"], { cwd: repoRoot, encoding: "utf8" })
    .split("\n")
    .filter(Boolean)
    .filter((relativePath) => fs.existsSync(path.join(repoRoot, relativePath)))
    .filter((relativePath) => {
      if (relativePath.startsWith(".omo/") || relativePath.startsWith(".private/")) return false;
      if (relativePath.includes("/fixtures/")) return false;
      return (
        relativePath.endsWith(".md") ||
        relativePath.endsWith(".mdx") ||
        relativePath.endsWith(".txt") ||
        relativePath.endsWith(".sh") ||
        relativePath.endsWith(".js") ||
        relativePath.endsWith(".yml") ||
        relativePath.endsWith(".yaml")
      );
    });
}

function assertOliveYoungCloneFallbackCommands(doc, label) {
  assert.match(doc, /node dist\/bin\.js health/, `${label} should document the runnable local health command`);
  assert.match(
    doc,
    /node dist\/bin\.js get \/api\/oliveyoung\/stores --keyword 명동 --limit 5 --json/,
    `${label} should document the runnable local store lookup command`,
  );
  assert.match(
    doc,
    /node dist\/bin\.js get \/api\/oliveyoung\/products --keyword 선크림 --size 5 --json/,
    `${label} should document the runnable local product lookup command`,
  );
  assert.match(
    doc,
    /node dist\/bin\.js get \/api\/oliveyoung\/inventory --keyword 선크림 --storeKeyword 명동 --size 5 --json/,
    `${label} should document the runnable local inventory lookup command`,
  );
  assert.doesNotMatch(doc, /^\s*npx daiso\b/m, `${label} should not publish broken clone-local npx commands`);
}

function assertOliveYoungCloneFallbackShorthand(doc, label) {
  assert.match(
    doc,
    /git clone https:\/\/github\.com\/hmmhmmhm\/daiso-mcp\.git && cd daiso-mcp && npm install && npm run build/,
    `${label} should include a runnable shorthand that changes into the clone before install/build`,
  );
  assert.doesNotMatch(
    doc,
    /git clone https:\/\/github\.com\/hmmhmmhm\/daiso-mcp\.git && npm install && npm run build/,
    `${label} should not publish the broken shorthand that skips cd daiso-mcp`,
  );
}

function extractQuotedEntries(block, indent) {
  return block
    .split("\n")
    .map((line) => line.match(new RegExp(`^ {${indent}}"([^"]+)":\\s*(.+?)(?:,)?$`)))
    .filter(Boolean)
    .map(([, key, value]) => [key, value.trim()]);
}

function findPrintedObjectBlock(doc, carrier) {
  const block = [...doc.matchAll(/print\(json\.dumps\(\{\n([\s\S]*?)\n\}, ensure_ascii=False, indent=2\)\)/g)]
    .map((match) => match[1])
    .find((candidate) => candidate.includes(`"carrier": "${carrier}"`));

  assert.ok(block, `expected ${carrier} normalized JSON example`);
  return block;
}

function findRecentEventsBlock(doc, carrier) {
  const block = [...doc.matchAll(/normalized_events = \[\n\s*\{\n([\s\S]*?)\n\s*\}\n\s*for [^\n]+ in events\n\]/g)]
    .map((match) => match[1])
    .find((candidate) => candidate.includes('"status_code":') === (carrier === "cj"));

  assert.ok(block, `expected ${carrier} recent_events example`);
  return block;
}

function findJsonFenceAfterLabel(doc, label) {
  return JSON.parse(findJsonFenceTextAfterLabel(doc, label));
}

function findJsonFenceTextAfterLabel(doc, label) {
  const escaped = escapeRegex(label);
  const match = doc.match(new RegExp(`${escaped}[\\s\\S]*?\\\`\\\`\\\`json\\n([\\s\\S]*?)\\n\\\`\\\`\\\``));

  assert.ok(match, `expected JSON example after "${label}"`);
  return match[1];
}

function assertSampleProvenance(doc, sectionLabel, expected, docLabel) {
  const escapedSectionLabel = escapeRegex(sectionLabel);
  const escapedVerifiedAt = escapeRegex(expected.verified_at);
  const escapedInvoice = escapeRegex(expected.invoice);

  assert.match(
    doc,
    new RegExp(
      `${escapedSectionLabel}[\\s\\S]*?아래 값은 ${escapedVerifiedAt} 기준 live smoke test\\(\\x60${escapedInvoice}\\x60\\)에서 확인한 정규화 결과다\\.\\n\\n\\\`\\\`\\\`json`,
    ),
    `${docLabel} ${sectionLabel} provenance line must stay pinned to the verified smoke-test date and invoice`,
  );
}

function assertSanitizedPublicOutput(output, label) {
  const serialized = JSON.stringify(output);

  assert.doesNotMatch(serialized, /\bTEL\b/i, `${label} must not leak TEL fragments`);
  assert.doesNotMatch(
    serialized,
    /\d{2,4}[.\-]\d{3,4}[.\-]\d{4}/,
    `${label} must not leak phone-number-like strings anywhere in the published sample`,
  );
  assert.doesNotMatch(serialized, /crgNm/, `${label} must not leak CJ assignee/source fields`);
  assert.doesNotMatch(serialized, /sender/i, `${label} must not leak sender fields`);
  assert.doesNotMatch(serialized, /receiver/i, `${label} must not leak receiver fields`);
  assert.doesNotMatch(serialized, /delivered_to/i, `${label} must not leak delivered_to fields`);
}

function assertKakaoBarNearbySadangSmokeSnapshot(smoke, label) {
  assert.equal(smoke.anchor.name, "사당1동먹자골목상점가", `${label} anchor should stay on the verified area landmark`);
  assert.equal(smoke.meta.openNowCount, 4, `${label} should publish the verified open-now count`);
  assert.deepEqual(
    smoke.items.map((item) => item.name),
    ["우미노식탁", "방배을지로골뱅이술집포차 사당역점", "커먼테이블"],
    `${label} should keep the verified top-3 ordering`,
  );
}

test("root npm test script includes the skill docs regression suite", () => {
  const packageJson = JSON.parse(read("package.json"));

  assert.match(packageJson.scripts.test, /node --test scripts\/skill-docs\.test\.js/);
});

// Skills that have migrated to the @nomadamas/k-skill CLI adapter keep their
// source in skill.json/instruction.md and publish a generated stub SKILL.md.
function cliManagedSkills() {
  return fs
    .readdirSync(repoRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => fs.existsSync(path.join(repoRoot, name, "skill.json")))
    .sort();
}

test("every top-level skill embeds the canonical portable runtime contract or a CLI stub", () => {
  const canonical = findSection(read("docs/adding-a-skill.md"), "## Runtime contract (required)").trim();
  const cliManaged = new Set(cliManagedSkills());
  const skillDirs = fs
    .readdirSync(repoRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => fs.existsSync(path.join(repoRoot, name, "SKILL.md")))
    .sort();

  assert.equal(skillDirs.length, 75);

  for (const skillName of skillDirs) {
    const skill = readRaw(path.join(skillName, "SKILL.md"));

    if (cliManaged.has(skillName)) {
      assert.match(skill, /k-skill:cli-stub/, `${skillName} must be a generated CLI stub`);
      assert.match(
        skill,
        new RegExp(`npx -y @nomadamas/k-skill@0 instruct ${escapeRegex(skillName)}`),
        `${skillName} stub must invoke the pinned-major CLI`,
      );
      continue;
    }

    assert.ok(skill.includes(canonical), `${skillName} must embed the canonical portable runtime contract`);
    assert.equal(
      (skill.match(/^## Runtime contract \(required\)$/gm) ?? []).length,
      1,
      `${skillName} must contain exactly one portable runtime contract`,
    );
  }
});

test("CLI-managed skills keep source, stub safety floor, and bundled copies aligned", () => {
  const cliManaged = cliManagedSkills();

  assert.ok(cliManaged.length >= 5, "expected at least the five pilot skills to be CLI-managed");

  const { SAFETY_FLOOR } = require("./generate-skill-stubs.js");

  for (const skillName of cliManaged) {
    const stub = readRaw(path.join(skillName, "SKILL.md"));
    const manifest = readJson(path.join(skillName, "skill.json"));

    assert.equal(manifest.name, skillName, `${skillName}/skill.json name must match the directory`);
    assert.ok(
      fs.existsSync(path.join(repoRoot, skillName, "instruction.md")),
      `${skillName} must keep its instruction.md source`,
    );
    assert.ok(stub.includes(SAFETY_FLOOR), `${skillName} stub must keep the static safety floor`);
    assert.match(stub, /clarify|approval/, `${skillName} stub must state the approval boundary`);

    for (const relative of ["skill.json", "instruction.md"]) {
      const source = readRaw(path.join(skillName, relative));
      const bundled = readRaw(path.join("packages", "k-skill-cli", "skills", skillName, relative));

      assert.equal(bundled, source, `packages/k-skill-cli/skills/${skillName}/${relative} must match the source`);
    }
  }

  // Staleness gates: regenerating and re-syncing must be no-ops.
  childProcess.execFileSync("node", [path.join(__dirname, "generate-skill-stubs.js"), "--check"], { cwd: repoRoot });
  childProcess.execFileSync(
    "node",
    [path.join(__dirname, "migrate-cli-asset-instructions.js"), "--check"],
    { cwd: repoRoot },
  );
  childProcess.execFileSync("node", [path.join(__dirname, "sync-cli-skills.js"), "--check"], { cwd: repoRoot });
});

test("actionable skills publish a Dolshoi action path", () => {
  const cliManaged = new Set(cliManagedSkills());
  const actionableSkills = [
    "catchtable-sniper",
    "court-auction-notice-search",
    "flight-ticket-search",
    "foresttrip-vacancy",
    "g2b-order-plan-search",
    "hipass-receipt",
    "hola-poke-yeoksam",
    "intercity-bus-booking",
    "iros-registry-automation",
    "job-posting-match",
    "jobkorea-talent-search",
    "lh-notice-search",
    "library-book-search",
    "lovebug-report",
    "market-kurly-search",
    "myrealtrip-search",
    "naver-shopping-search",
    "nhis-care-checkup-search",
    "nts-business-registration",
    "nts-tax-delinquency",
    "popbill",
    "sh-notice-search",
    "srt-booking",
    "subway-lost-property",
    "ticket-availability",
    "toss-securities",
  ];

  for (const skillName of actionableSkills) {
    if (cliManaged.has(skillName)) continue; // action path now lives in the CLI-assembled instructions

    const skill = read(path.join(skillName, "SKILL.md"));

    assert.match(skill, /^## Dolshoi action path$/m, `${skillName} should document its Dolshoi action path`);
    assert.match(skill, /clarify/, `${skillName} should document irreversible-action approval`);
  }
});

test("runtime action audit covers every top-level skill exactly once", () => {
  const audit = findSection(read("docs/runtime-action-audit.md"), "## Complete catalog");
  const skillDirs = fs
    .readdirSync(repoRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => fs.existsSync(path.join(repoRoot, name, "SKILL.md")))
    .sort();

  for (const skillName of skillDirs) {
    const matches = audit.match(new RegExp(`^\\| \\\`${escapeRegex(skillName)}\\\` \\|`, "gm")) ?? [];

    assert.equal(matches.length, 1, `${skillName} must appear exactly once in the runtime action audit`);
  }
});


test("repository publishes Korean contribution guidance for external contributors", () => {
  const contributingPath = path.join(repoRoot, "CONTRIBUTING.md");

  assert.ok(fs.existsSync(contributingPath), "expected CONTRIBUTING.md to exist");

  const contributing = read("CONTRIBUTING.md");

  assert.match(contributing, /^# 기여 가이드$/m);
  assert.match(contributing, /PR 코멘트, 이슈, 리뷰 등 모든 소통은 한국어로 진행/);
  assert.match(contributing, /PR의 대상 브랜치는 반드시 `dev`/);
  assert.match(contributing, /`main` 브랜치로 PR을 만들 수 있는 사람은 `@vkehfdl1`뿐/);
  assert.match(contributing, /스킬을 추가하거나 변경할 때는 관련 기능 문서와 `README\.md`의 표/);
  assert.match(contributing, /npm 패키지를 수정할 때는 Changesets/);
  assert.match(contributing, /Changeset 파일의 존재 여부를 테스트로 검증하지 않는다/);
  assert.match(contributing, /`package\.json`과 `package-lock\.json`의 `version` 필드를 테스트에서 고정하지 않는다/);
  assert.match(contributing, /`name`, `license`, `engines\.node`, workspace link metadata/);
  assert.match(contributing, /현재 구현이 registry token 기반인 경우에도 신규 또는 재설계 흐름은 trusted publishing\/OIDC를 우선/);
  assert.match(contributing, /신규 proxy route는 upstream이 API key를 요구하는 무료 API인 경우에만 `k-skill-proxy` 경유를 검토/);
  assert.match(contributing, /인증 없이 동작하는 공개 read-only endpoint는 기본적으로 사용자 머신에서 직접 호출/);
  assert.doesNotMatch(contributing, /무료 API이고 1일 리미트가 충분한 경우/);
  assert.match(contributing, /유료 API/);
  assert.match(contributing, /`k-skill-proxy`를 타지 않도록 설계/);
  assert.match(contributing, /릴리스나 패키징 관련 변경은 `npm run ci`/);
  assert.match(contributing, /`~\/\.claude\/skills\/<skill-name>`/);
  assert.match(contributing, /`~\/\.agents\/skills\/<skill-name>`/);
  assert.match(contributing, /gpu01/);
  assert.match(contributing, /systemd/);
  assert.match(contributing, /gpu01 app directory의 `\.env`/);
  assert.match(contributing, /`main`에 머지된 뒤에만 프로덕션에 반영/);
});




test("hwp skill documents kordoc-based parsing and supported operations", () => {
  const skillPath = path.join(repoRoot, "hwp", "SKILL.md");

  assert.ok(fs.existsSync(skillPath), "expected hwp/SKILL.md to exist");

  const skill = read(path.join("hwp", "SKILL.md"));

  assert.match(skill, /^name: hwp$/m);
  assert.match(skill, /\bkordoc\b/);
  assert.doesNotMatch(skill, /@ohah\/hwpjs/);
  assert.doesNotMatch(skill, /\bhwp-mcp\b/);
  assert.match(skill, /JSON/i);
  assert.match(skill, /Markdown/i);
  assert.match(skill, /image/i);
  assert.match(skill, /(batch|배치)/i);
  assert.match(skill, /HWPX/i);
  assert.match(skill, /(역변환|되돌려)/);
  assert.match(skill, /(비교|compare)/i);
  assert.match(skill, /pdfjs-dist/);
  assert.match(skill, /(extractFormFields|양식 필드)/);
  assert.doesNotMatch(skill, /fillForm/);
  assert.doesNotMatch(skill, /kordoc fill/);
  assert.doesNotMatch(skill, /kordoc mcp/);
});






test("public-restroom-nearby docs describe the maxDistanceMeters distance cap", () => {
  const featureDoc = read(path.join("docs", "features", "public-restroom-nearby.md"));
  const packageReadme = read(path.join("packages", "public-restroom-nearby", "README.md"));

  assert.match(featureDoc, /maxDistanceMeters/);
  assert.match(featureDoc, /100m/);
  assert.match(packageReadme, /maxDistanceMeters/);
  assert.match(packageReadme, /100m/);
});


test("lck-analytics docs and skill credit the original author and reference repo", () => {
  const skill = read(path.join("lck-analytics", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "lck-analytics.md"));
  const packageReadme = read(path.join("packages", "lck-analytics", "README.md"));
  const sources = read(path.join("docs", "sources.md"));

  for (const doc of [skill, featureDoc, packageReadme]) {
    assert.match(doc, /jerjangmin/);
    assert.match(doc, /https:\/\/github\.com\/jerjangmin\/share\/tree\/main\/SKILL\/lck-analytics/);
    assert.match(doc, /Riot|LoL Esports|Oracle(?:'s)? Elixir/i);
  }

  assert.match(sources, /https:\/\/github\.com\/jerjangmin\/share\/tree\/main\/SKILL\/lck-analytics/);
});








test("proxy deployment script and docs stay aligned with gpu01 automation", () => {
  const deployScript = read(path.join("scripts", "deploy-k-skill-proxy-gpu01.sh"));
  const agents = read("AGENTS.md");
  const deployDoc = read(path.join("docs", "deploy-k-skill-proxy.md"));
  const featureDoc = read(path.join("docs", "features", "k-skill-proxy.md"));
  const packageReadme = read(path.join("packages", "k-skill-proxy", "README.md"));
  const dockerfile = read(path.join("packages", "k-skill-proxy", "Dockerfile"));
  const dockerignore = read(".dockerignore");
  const npmReleaseWorkflow = read(path.join(".github", "workflows", "release-npm.yml"));
  const proxyPackage = JSON.parse(read(path.join("packages", "k-skill-proxy", "package.json")));

  assert.match(deployScript, /DEPLOY_REF="\$\{KSKILL_PROXY_DEPLOY_REF:-origin\/main\}"/);
  assert.match(deployScript, /npm --prefix "\$REPO_DIR" run test --workspace k-skill-proxy/);
  assert.match(deployScript, /tar -C "\$APP_DIR" -czf "\$backup"/);
  assert.match(deployScript, /systemctl --user restart "\$SERVICE_NAME"/);
  assert.match(deployScript, /health_check http:\/\/127\.0\.0\.1:8080\/health/);
  assert.match(deployScript, /health_check https:\/\/k-skill-proxy\.nomadamas\.org\/health/);
  assert.match(deployScript, /printf '%s\\n' "\$target_sha" > "\$APP_DIR\/deployed-sha"/);
  assert.match(dockerfile, /COPY package\.json package-lock\.json/);
  assert.match(dockerfile, /npm ci --omit=dev --workspace k-skill-proxy/);
  assert.match(dockerignore, /^gha-creds-\*\.json$/m);
  assert.doesNotMatch(npmReleaseWorkflow, /^\s+workflow_dispatch:/m);
  assert.equal(proxyPackage.engines.node, ">=20");

  for (const doc of [agents, deployDoc, featureDoc, packageReadme]) {
    assert.match(doc, /gpu01/i);
    assert.match(doc, /main/i);
  }

  assert.match(agents, /scripts\/deploy-k-skill-proxy-gpu01\.sh/);
  assert.match(deployDoc, /systemd/i);
  assert.match(deployDoc, /flock/);
  assert.match(deployDoc, /rollback/i);
  assert.match(deployDoc, /deployed-sha/);
});




test("ktx-booking helper python regression tests pass", () => {
  const result = childProcess.spawnSync(
    "python3",
    ["-m", "unittest", "discover", "-s", "scripts", "-p", "test_ktx_booking.py"],
    {
      cwd: repoRoot,
      encoding: "utf8",
      env: { ...process.env, PYTHONNOUSERSITE: "1" },
    },
  );

  assert.equal(
    result.status,
    0,
    `expected python KTX helper regression tests to pass\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`,
  );
});


test("geeknews-search docs lock the RSS-first list-search-detail workflow", () => {
  const skill = read(path.join("geeknews-search", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "geeknews-search.md"));

  for (const doc of [skill, featureDoc]) {
    assert.match(doc, /feeds\.feedburner\.com\/geeknews-feed/);
    assert.match(doc, /@nomadamas\/k-skill@0 exec geeknews-search scripts\/geeknews_search\.py -- list/);
    assert.match(doc, /@nomadamas\/k-skill@0 exec geeknews-search scripts\/geeknews_search\.py -- search/);
    assert.match(doc, /@nomadamas\/k-skill@0 exec geeknews-search scripts\/geeknews_search\.py -- detail/);
    assert.match(doc, /RSS-first|RSS first|RSS 피드/);
    assert.match(doc, /read-only|읽기 전용/);
  }
});


test("subway-lost-property docs lock the official LOST112 guidance flow", () => {
  const skill = read(path.join("subway-lost-property", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "subway-lost-property.md"));

  for (const doc of [skill, featureDoc]) {
    assert.match(doc, /LOST112/);
    assert.match(doc, /seoulmetro\.co\.kr\/kr\/page\.do\?menuIdx=541/);
    assert.match(doc, /@nomadamas\/k-skill@0 exec subway-lost-property scripts\/subway_lost_property\.py --/);
    assert.match(doc, /SITE=V/);
    assert.match(doc, /안내형|하이브리드/);
  }
});




test("delivery-tracking skill documents official CJ and ePost flows with extension guidance", () => {
  const skillPath = path.join(repoRoot, "delivery-tracking", "SKILL.md");

  assert.ok(fs.existsSync(skillPath), "expected delivery-tracking/SKILL.md to exist");

  const skill = read(path.join("delivery-tracking", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "delivery-tracking.md"));

  assert.match(skill, /^name: delivery-tracking$/m);

  for (const doc of [skill, featureDoc]) {
    assert.match(doc, /https:\/\/www\.cjlogistics\.com\/ko\/tool\/parcel\/tracking/);
    assert.match(doc, /tracking-detail/);
    assert.match(doc, /paramInvcNo/);
    assert.match(doc, /_csrf/);
    assert.match(doc, /10자리 또는 12자리/);
    assert.match(doc, /https:\/\/service\.epost\.go\.kr\/trace\.RetrieveRegiPrclDeliv\.postal\?sid1=/);
    assert.match(doc, /trace\.RetrieveDomRigiTraceList\.comm/);
    assert.match(doc, /sid1/);
    assert.match(doc, /13자리/);
    assert.match(doc, /curl --http1\.1 --tls-max 1\.2/);
    assert.match(doc, /carrier adapter/i);
    assert.match(doc, /다른 택배사/);
  }

  assert.match(skill, /1234567890/);
  assert.match(skill, /1234567890123/);
  assert.match(skill, /python3/);
  assert.match(featureDoc, /JSON/);
  assert.match(featureDoc, /HTML/);
});







test("daiso-product-search docs record the shipped feature and official sources", () => {
  const roadmap = read(path.join("docs", "roadmap.md"));
  const sources = read(path.join("docs", "sources.md"));

  assert.match(roadmap, /다이소 상품 조회 스킬 출시/);
  assert.match(sources, /https:\/\/www\.daisomall\.co\.kr\/api\/ms\/msg\/selStr/);
  assert.match(sources, /https:\/\/www\.daisomall\.co\.kr\/ssn\/search\/SearchGoods/);
  assert.match(sources, /https:\/\/www\.daisomall\.co\.kr\/api\/pd\/pdh\/selStrPkupStck/);
});




test("market-kurly-search skill and docs describe the unauthenticated Kurly search and detail flow", () => {
  const skill = read(path.join("market-kurly-search", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "market-kurly-search.md"));

  assert.match(skill, /^name: market-kurly-search$/m);
  assert.match(skill, /^description: .*마켓컬리.*상품.*가격.*$/m);

  for (const doc of [skill, featureDoc]) {
    assert.match(doc, /api\.kurly\.com\/search\/v4\/sites\/market\/normal-search/);
    assert.match(doc, /api\.kurly\.com\/search\/v3\/sites\/market\/normal-search\/count/);
    assert.match(doc, /www\.kurly\.com\/goods\/<productNo>|www\.kurly\.com\/goods\/5063110/);
    assert.match(doc, /로그인 없이|비로그인/);
    assert.match(doc, /현재 가격|할인/);
    assert.match(doc, /품절 여부|판매 상태/);
    assert.match(doc, /가격.*달라질 수|시점에 따라 달라질 수/u);
    assert.match(doc, /주문|장바구니/);
    assert.match(doc, /보수적으로|보수적/);
  }
});

test("market-kurly-search package exposes reusable search/count/detail helpers", () => {
  const pkg = require(path.join(repoRoot, "packages", "market-kurly-search", "src", "index.js"));

  assert.equal(typeof pkg.searchProducts, "function");
  assert.equal(typeof pkg.countProducts, "function");
  assert.equal(typeof pkg.getProductDetail, "function");
});


test("olive-young install docs warn about intermittent public endpoint failures and direct users to retry or clone fallback", () => {
  const install = read(path.join("docs", "install.md"));
  const quickstart = findSection(install, "### `olive-young-search` upstream CLI quickstart");

  assert.match(install, /olive-young-search/);
  assert.match(install, /5xx\/503/);
  assert.match(install, /재시도|retry/i);
  assert.match(install, /clone fallback|git clone https:\/\/github\.com\/hmmhmmhm\/daiso-mcp\.git/i);
  assertOliveYoungCloneFallbackShorthand(quickstart, "olive-young install quickstart");
  assertOliveYoungCloneFallbackCommands(quickstart, "olive-young install quickstart");
});











test("root pack:dry-run script covers all publishable workspaces", () => {
  const packageJson = readJson("package.json");
  const packScript = packageJson.scripts["pack:dry-run"];
  const publishableWorkspaces = fs
    .readdirSync(path.join(repoRoot, "packages"), { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join("packages", entry.name, "package.json"))
    .filter((packagePath) => fs.existsSync(path.join(repoRoot, packagePath)))
    .map((packagePath) => readJson(packagePath))
    .filter((workspacePackage) => workspacePackage.private !== true)
    .map((workspacePackage) => workspacePackage.name);

  assert.ok(publishableWorkspaces.length > 0);
  for (const workspaceName of publishableWorkspaces) {
    assert.match(packScript, new RegExp(`workspace ${escapeRegex(workspaceName)}(?:\\s|$)`));
  }
});


test("donation-place-search install docs include the skill and npm helper", () => {
  const install = read(path.join("docs", "install.md"));

  assert.match(install, /--skill donation-place-search/);
  assert.match(install, /npm install -g .*donation-place-search/);
});











test("unsupported naver map and blue ribbon skills are archived outside default docs", () => {
  const readme = read("README.md");
  const install = read(path.join("docs", "install.md"));
  const sources = read(path.join("docs", "sources.md"));
  const legacyReadmePath = path.join(repoRoot, "legacy", "README.md");
  const blueRibbonSkillPath = path.join(repoRoot, "legacy", "unsupported-skills", "blue-ribbon-nearby", "SKILL.md");
  const naverMapSkillPath = path.join(repoRoot, "legacy", "unsupported-skills", "naver-map-route", "SKILL.md");
  const blueRibbonDocPath = path.join(
    repoRoot,
    "legacy",
    "unsupported-skills",
    "blue-ribbon-nearby",
    "docs",
    "features",
    "blue-ribbon-nearby.md",
  );
  const naverMapDocPath = path.join(
    repoRoot,
    "legacy",
    "unsupported-skills",
    "naver-map-route",
    "docs",
    "features",
    "naver-map-route.md",
  );

  assert.ok(fs.existsSync(legacyReadmePath), "expected legacy/README.md to explain archived unsupported skills");
  assert.ok(fs.existsSync(blueRibbonSkillPath), "expected blue-ribbon-nearby SKILL.md to be preserved under legacy");
  assert.ok(fs.existsSync(naverMapSkillPath), "expected naver-map-route SKILL.md to be preserved under legacy");
  assert.ok(fs.existsSync(blueRibbonDocPath), "expected blue-ribbon-nearby feature doc to be preserved under legacy");
  assert.ok(fs.existsSync(naverMapDocPath), "expected naver-map-route feature doc to be preserved under legacy");
  assert.ok(!fs.existsSync(path.join(repoRoot, "blue-ribbon-nearby", "SKILL.md")));
  assert.ok(!fs.existsSync(path.join(repoRoot, "naver-map-route", "SKILL.md")));
  assert.ok(!fs.existsSync(path.join(repoRoot, "docs", "features", "blue-ribbon-nearby.md")));
  assert.ok(!fs.existsSync(path.join(repoRoot, "docs", "features", "naver-map-route.md")));

  for (const doc of [readme, install, sources]) {
    assert.doesNotMatch(doc, /blue-ribbon-nearby|naver-map-route/);
    assert.doesNotMatch(doc, /근처 블루리본 맛집|네이버맵 길찾기|네이버맵 자동차 길찾기/);
  }
});








test("fine-dust helper python regression tests pass", () => {
  const result = childProcess.spawnSync(
    "python3",
    ["-m", "unittest", "discover", "-s", "scripts", "-p", "test_fine_dust.py"],
    { cwd: repoRoot, encoding: "utf8" },
  );

  assert.equal(
    result.status,
    0,
    `expected python fine-dust helper regression tests to pass\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`,
  );
});



test("toss-securities skill documents the official Open API and tossctl fallback workflow", () => {
  const skillPath = path.join(repoRoot, "toss-securities", "SKILL.md");

  assert.ok(fs.existsSync(skillPath), "expected toss-securities/SKILL.md to exist");

  const skill = read(path.join("toss-securities", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "toss-securities.md"));

  assert.match(skill, /^name: toss-securities$/m);

  for (const doc of [skill, featureDoc]) {
    // Official Open API path (primary).
    assert.match(doc, /openapi\.tossinvest\.com|developers\.tossinvest\.com/);
    assert.match(doc, /TOSSINVEST_CLIENT_ID/);
    assert.match(doc, /X-Tossinvest-Account/);
    assert.match(doc, /\/oauth2\/token/);
    // tossctl fallback path (retained).
    assert.match(doc, /tossctl/);
    assert.match(doc, /JungHoonGhae\/tossinvest-cli/);
    assert.match(doc, /auth login/);
    assert.match(doc, /account summary/);
    assert.match(doc, /portfolio positions/);
    assert.match(doc, /quote get/);
    assert.match(doc, /watchlist list/);
    assert.match(doc, /read-only|조회 전용/u);
    assert.doesNotMatch(doc, /order place/);
  }
});

test("hipass-receipt skill documents the logged-in browser session contract", () => {
  const skillPath = path.join(repoRoot, "hipass-receipt", "SKILL.md");
  const packageReadmePath = path.join(repoRoot, "packages", "hipass-receipt", "README.md");

  assert.ok(fs.existsSync(skillPath), "expected hipass-receipt/SKILL.md to exist");
  assert.ok(fs.existsSync(packageReadmePath), "expected packages/hipass-receipt/README.md to exist");

  const skill = read(path.join("hipass-receipt", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "hipass-receipt.md"));
  const packageReadme = read(path.join("packages", "hipass-receipt", "README.md"));

  assert.match(skill, /^name: hipass-receipt$/m);
  assert.match(skill, /로그인은 반드시 사용자가 직접 해야 한다/);
  assert.match(skill, /Playwright persistent context|user-data-dir/);
  assert.match(skill, /세션이 만료되면 즉시 중단하고 다시 로그인/);
  assert.match(featureDoc, /20분/);
  assert.match(featureDoc, /영수증선택출력|영수증전체출력/);
  assert.match(featureDoc, /로그인된 브라우저 세션에서만 동작/);
  assert.match(featureDoc, /playwright-core/);
  assert.match(skill, /--encrypted-card-number/);
  assert.match(packageReadme, /buildUsageHistoryQuery/);
  assert.match(packageReadme, /parseUsageHistoryList/);
  assert.match(packageReadme, /inspectHipassPage/);
  assert.match(packageReadme, /playwright-core/);
});

test("toss-securities package exposes safe read-only official + tossctl helpers", () => {
  const pkg = require(path.join(repoRoot, "packages", "toss-securities", "src", "index.js"));

  // tossctl fallback wrapper (retained).
  assert.equal(typeof pkg.buildReadOnlyCommand, "function");
  assert.equal(typeof pkg.runReadOnlyCommand, "function");
  assert.equal(typeof pkg.getAccountSummary, "function");
  assert.equal(typeof pkg.getPortfolioPositions, "function");
  assert.equal(typeof pkg.getQuote, "function");
  assert.equal(typeof pkg.getQuoteBatch, "function");
  assert.equal(typeof pkg.listWatchlist, "function");

  // Official Open API client (primary).
  assert.equal(typeof pkg.issueAccessToken, "function");
  assert.equal(typeof pkg.getPrices, "function");
  assert.equal(typeof pkg.getHoldings, "function");
  assert.equal(typeof pkg.getBuyingPower, "function");
  assert.equal(typeof pkg.listOfficialAccounts, "function");
  assert.equal(typeof pkg.TossApiError, "function");
  assert.equal(typeof pkg.TossCredentialsError, "function");

  // Read-only safety contract: no order mutation helpers.
  assert.equal(pkg.placeOrder, undefined);
  assert.equal(pkg.modifyOrder, undefined);
  assert.equal(pkg.cancelOrder, undefined);
});


test("toss-securities package README stays aligned with the official-first read-only contract", () => {
  const packageReadme = read(path.join("packages", "toss-securities", "README.md"));

  // Official Open API path (primary).
  assert.match(packageReadme, /official.*Open API|공식 Open API/i);
  assert.match(packageReadme, /TOSSINVEST_CLIENT_ID/);
  assert.match(packageReadme, /X-Tossinvest-Account/);
  // tossctl fallback path (retained).
  assert.match(packageReadme, /read-only tossctl wrapper/i);
  assert.match(packageReadme, /brew tap JungHoonGhae\/tossinvest-cli/);
  assert.match(packageReadme, /account summary/);
  assert.match(packageReadme, /quote get/);
  assert.match(packageReadme, /order place/);
  assert.match(packageReadme, /지원하지 않음|not supported/u);
});

test("hipass-receipt package README and npm metadata stay aligned with the helper contract", () => {
  const packageReadme = read(path.join("packages", "hipass-receipt", "README.md"));
  const packageJson = readJson(path.join("packages", "hipass-receipt", "package.json"));

  assert.equal(packageJson.name, "hipass-receipt");
  assert.match(packageJson.description, /Hi-Pass/);
  assert.ok(packageJson.files.includes("test/fixtures"));
  assert.match(packageReadme, /logged-in browser session/i);
  assert.match(packageReadme, /Playwright/);
  assert.equal(typeof packageJson.dependencies?.["playwright-core"], "string");
  assert.match(packageReadme, /playwright-core/);
  assert.match(packageReadme, /buildReceiptRequest/);
  assert.match(packageReadme, /test\/fixtures\/usage-history-list\.html/);
});

test("hipass-receipt pack dry-run ships fixture-demo assets for the published README workflow", () => {
  const packResult = JSON.parse(
    childProcess.execFileSync(process.platform === "win32" ? "npm.cmd" : "npm", ["pack", "--workspace", "hipass-receipt", "--json", "--dry-run"], {
      cwd: repoRoot,
      encoding: "utf8",
      shell: process.platform === "win32"
    }),
  );

  const files = packResult[0]?.files?.map((entry) => entry.path) || [];
  assert.ok(files.includes("test/fixtures/usage-history-list.html"));
  assert.ok(files.includes("test/fixtures/login-page.html"));
  assert.ok(files.includes("README.md"));
});

test("pack:dry-run includes the toss-securities workspace", () => {
  const packageJson = JSON.parse(read("package.json"));

    assert.match(packageJson.scripts["pack:dry-run"], /workspace toss-securities/);
    assert.match(packageJson.scripts["pack:dry-run"], /workspace hipass-receipt/);
  });

test("package-lock captures the toss-securities workspace metadata for npm ci", () => {
  const packageLock = readJson("package-lock.json");

  assert.deepEqual(packageLock.packages[""].workspaces, ["packages/*"]);
  assert.deepEqual(packageLock.packages["node_modules/toss-securities"], {
    resolved: "packages/toss-securities",
    link: true,
  });
  assert.equal(packageLock.packages["packages/toss-securities"].license, "MIT");
  assert.equal(packageLock.packages["packages/toss-securities"].engines.node, ">=18");
});




test("joseon-sillok-search install payload includes the documented helper command", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "joseon-sillok-"));
  const installedSkillPath = path.join(tempRoot, "joseon-sillok-search");
  const bundledHelperPath = path.join(installedSkillPath, "scripts", "sillok_search.py");

  try {
    fs.cpSync(path.join(repoRoot, "joseon-sillok-search"), installedSkillPath, { recursive: true });

    assert.ok(fs.existsSync(bundledHelperPath), "expected joseon-sillok-search/scripts/sillok_search.py to exist");

    const helpText = childProcess.execFileSync("python3", ["scripts/sillok_search.py", "--help"], {
      cwd: installedSkillPath,
      encoding: "utf8",
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    });

    assert.match(helpText, /Search Joseon Sillok records from sillok\.history\.go\.kr/);
    assert.match(helpText, /--query/);
    assert.match(helpText, /--king/);
  } finally {
    fs.rmSync(tempRoot, { recursive: true, force: true });
  }
});
















test("cheap-gas-nearby skill docs require location-first prompts and official Opinet surfaces", () => {
  const skill = read(path.join("cheap-gas-nearby", "SKILL.md"));
  const featureDoc = read(path.join("docs", "features", "cheap-gas-nearby.md"));

  for (const doc of [skill, featureDoc]) {
    assert.match(doc, /현재 위치를 알려주세요/);
    assert.match(doc, /OPINET_API_KEY/);
    assert.match(doc, /aroundAll\.do/);
    assert.match(doc, /detailById\.do/);
    assert.match(doc, /areaCode\.do/);
    assert.match(doc, /휘발유|경유/);
    assert.match(doc, /KATEC/);
    assert.match(doc, /카카오맵|Kakao Map/);
  }
});



test("MFDS public-health skill docs require interview-first safety flow and official endpoints", () => {
  const drugSkill = read(path.join("mfds-drug-safety", "SKILL.md"));
  const foodSkill = read(path.join("mfds-food-safety", "SKILL.md"));
  const drugFeatureDoc = read(path.join("docs", "features", "mfds-drug-safety.md"));
  const foodFeatureDoc = read(path.join("docs", "features", "mfds-food-safety.md"));
  const sources = read(path.join("docs", "sources.md"));
  const proxyReadme = read(path.join("packages", "k-skill-proxy", "README.md"));
  const proxyDoc = read(path.join("docs", "features", "k-skill-proxy.md"));

  for (const doc of [drugSkill, drugFeatureDoc]) {
    assert.match(doc, /증상.*바로 단정하지 말고.*먼저 되묻/);
    assert.match(doc, /호흡곤란|의식저하|심한 발진/);
    assert.match(doc, /DrbEasyDrugInfoService\/getDrbEasyDrugList/);
    assert.match(doc, /SafeStadDrugService\/getSafeStadDrugInq/);
    assert.match(doc, /KSKILL_PROXY_BASE_URL|k-skill-proxy\.nomadamas\.org/);
    assert.match(doc, /사용자.*시크릿 없음|사용자 API key 없이/u);
    assert.match(doc, /DATA_GO_KR_API_KEY.*프록시 운영 서버/u);
    assert.match(doc, /\/v1\/mfds\/drug-safety\/lookup/);
    assert.match(
      doc,
      /@nomadamas\/k-skill@0 exec mfds-drug-safety scripts\/mfds_drug_safety\.py --/,
    );
  }

  for (const doc of [foodSkill, foodFeatureDoc]) {
    assert.match(doc, /증상.*바로 단정하지 말고.*먼저 되묻/);
    assert.match(doc, /혈변|탈수|호흡곤란/);
    assert.match(doc, /PrsecImproptFoodInfoService03\/getPrsecImproptFoodList01/);
    assert.match(doc, /I0490/);
    assert.match(doc, /KSKILL_PROXY_BASE_URL|k-skill-proxy\.nomadamas\.org/);
    assert.match(doc, /사용자.*시크릿 없음|사용자 API key 없이/u);
    assert.match(doc, /DATA_GO_KR_API_KEY.*프록시 운영 서버/u);
    assert.match(doc, /FOODSAFETYKOREA_API_KEY/);
    assert.match(doc, /\/v1\/mfds\/food-safety\/search/);
    assert.match(
      doc,
      /@nomadamas\/k-skill@0 exec mfds-food-safety scripts\/mfds_food_safety\.py --/,
    );
    assert.match(doc, /https:\/\/openapi\.foodsafetykorea\.go\.kr\/api\/sample\/I0490\/json\/1\/5/);
    assert.doesNotMatch(doc, /http:\/\/openapi\.foodsafetykorea\.go\.kr/);
  }

  assert.match(sources, /https:\/\/openapi\.foodsafetykorea\.go\.kr\/api\/sample\/I0490\/json\/1\/5/);
  assert.doesNotMatch(sources, /http:\/\/openapi\.foodsafetykorea\.go\.kr/);
  for (const doc of [proxyReadme, proxyDoc]) {
    assert.match(doc, /\/v1\/mfds\/drug-safety\/lookup/);
    assert.match(doc, /\/v1\/mfds\/food-safety\/search/);
    assert.match(doc, /FOODSAFETYKOREA_API_KEY/);
  }
});











test("korean-privacy-terms feature doc documents the thin-wrapper install flow and legal disclaimer", () => {
  const featureDoc = read(path.join("docs", "features", "korean-privacy-terms.md"));

  assert.match(featureDoc, /kimlawtech\/korean-privacy-terms/);
  assert.match(featureDoc, /Apache-2\.0/);
  assert.match(featureDoc, /~\/\.claude\/skills\/korean-privacy-terms/);
  assert.match(featureDoc, /~\/\.agents\/skills\/korean-privacy-terms/);
  assert.match(featureDoc, /scripts\/install\.sh/);
  assert.match(featureDoc, /scripts\/upstream\.pin/);
  assert.match(featureDoc, /참고용 초안/);
  assert.match(featureDoc, /법률 자문/);
  assert.match(featureDoc, /변호사 검토/);
  assert.match(featureDoc, /2026\.9\.11/);
  assert.match(featureDoc, /Next\.js/);
});







test("korean-jangbu-for feature doc documents source-first use and mandatory attribution", () => {
  const featureDoc = read(path.join("docs", "features", "korean-jangbu-for.md"));

  assert.match(featureDoc, /kimlawtech\/korean-jangbu-for/);
  assert.match(featureDoc, /https:\/\/github\.com\/kimlawtech\/korean-jangbu-for/);
  assert.match(featureDoc, /@kimlawtech/);
  assert.match(featureDoc, /SpeciAI/);
  assert.match(featureDoc, /Apache-2\.0/);
  assert.match(featureDoc, /~\/\.claude\/skills\/korean-jangbu-for/);
  assert.match(featureDoc, /~\/\.agents\/skills\/korean-jangbu-for/);
  assert.match(featureDoc, /scripts\/install\.sh/);
  assert.match(featureDoc, /scripts\/upstream\.pin/);
  assert.match(featureDoc, /CODEF/);
  assert.match(featureDoc, /BYOK/);
  assert.match(featureDoc, /세무사 검토/);
  assert.match(featureDoc, /공인회계사/);
});






test("k-skill-rhwp package ships CLI bin, WASM-init shim, and minor semver changeset", () => {
  const packagePath = path.join(repoRoot, "packages", "k-skill-rhwp", "package.json");
  assert.ok(fs.existsSync(packagePath), "expected packages/k-skill-rhwp/package.json");
  const pkg = JSON.parse(fs.readFileSync(packagePath, "utf8"));

  assert.equal(pkg.name, "k-skill-rhwp");
  assert.ok(pkg.bin && pkg.bin["k-skill-rhwp"] === "bin/k-skill-rhwp.js", "expected bin mapping");
  assert.ok(pkg.dependencies && pkg.dependencies["@rhwp/core"], "expected @rhwp/core dependency");
  assert.ok(pkg.engines && /\^|>=\s*1[89]/.test(pkg.engines.node || ""), "expected Node 18+");
  assert.ok(
    fs.existsSync(path.join(repoRoot, "packages", "k-skill-rhwp", "src", "wasm-init.js")),
    "expected src/wasm-init.js"
  );
  assert.ok(
    fs.existsSync(path.join(repoRoot, "packages", "k-skill-rhwp", "bin", "k-skill-rhwp.js")),
    "expected bin/k-skill-rhwp.js"
  );

});

const README_SKILL_NAME_COLUMN_MAPPING = [
  ["SRT 예매", "srt-booking"],
  ["KTX 예매", "ktx-booking"],
  ["카카오톡 Mac 아카이브 검색", "kakaotalk-mac"],
  ["서울 지하철 도착정보 조회", "seoul-subway-arrival"],
  ["지하철 분실물 조회", "subway-lost-property"],
  ["긱뉴스 조회", "geeknews-search"],
  ["한국 날씨 조회", "korea-weather"],
  ["사용자 위치 미세먼지 조회", "fine-dust-location"],
  ["한강 수위 정보 조회", "han-river-water-level"],
  ["한국 법령 검색", "korean-law-search"],
  ["법인등기 신청 컨설팅", "corporate-registration-consulting"],
  ["한국 개인정보처리방침·이용약관 자동 생성", "korean-privacy-terms"],
  ["한국 부동산 실거래가 조회", "real-estate-search"],
  ["한국 주택 공시가격 조회", "housing-official-price"],
  ["LH 청약 공고문 조회", "lh-notice-search"],
  ["장학금 검색 및 조회", "korean-scholarship-search"],
  ["생활쓰레기 배출정보 조회", "household-waste-info"],
  ["학교 급식 식단 조회", "k-schoollunch-menu"],
  ["도서관 도서 조회", "library-book-search"],
  ["의약품 안전 체크", "mfds-drug-safety"],
  ["식품 안전 체크", "mfds-food-safety"],
  ["한국 주식 정보 조회", "korean-stock-search"],
  ["금감원 DART 전자공시 조회", "k-dart"],
  ["조선왕조실록 검색", "joseon-sillok-search"],
  ["국가유산 검색·행사 조회", "korean-heritage-search"],
  ["한국 특허 정보 검색", "korean-patent-search"],
  ["근처 가장 싼 주유소 찾기", "cheap-gas-nearby"],
  ["근처 공중화장실 찾기", "public-restroom-nearby"],
  ["근처 공영주차장 찾기", "parking-lot-search"],
  ["KBO 경기 결과 조회", "kbo-results"],
  ["KBL 경기 결과 조회", "kbl-results"],
  ["K리그 경기 결과 조회", "kleague-results"],
  ["LCK 경기 분석", "lck-analytics"],
  ["토스증권 조회", "toss-securities"],
  ["하이패스 영수증 발급", "hipass-receipt"],
  ["캐치테이블 예약 스나이핑", "catchtable-sniper"],
  ["로또 당첨 확인", "lotto-results"],
  ["HWP 문서 조회/변환", "hwp"],
  ["HWP 문서 편집", "rhwp-edit"],
  ["HWP 레이아웃·IR 디버깅", "rhwp-advanced"],
  ["근처 술집 조회", "kakao-bar-nearby"],
  ["우편번호 검색", "zipcode-search"],
  ["다이소 상품 조회", "daiso-product-search"],
  ["마켓컬리 상품 조회", "market-kurly-search"],
  ["올리브영 검색", "olive-young-search"],
  ["영화관 검색", "korean-cinema-search"],
  ["올라포케 역삼 포케", "hola-poke-yeoksam"],
  ["택배 배송조회", "delivery-tracking"],
  ["쿠팡 상품 검색", "coupang-product-search"],
  ["번개장터 검색", "bunjang-search"],
  ["중고차 가격 조회", "used-car-price-search"],
  ["한국어 맞춤법 검사", "korean-spell-check"],
  ["네이버 블로그 리서치", "naver-blog-research"],
  ["네이버 쇼핑 가격비교", "naver-shopping-search"],
  ["네이버 뉴스 검색", "naver-news-search"],
  ["한국일보 뉴스 조회", "hankookilbo-news"],
  ["한국어 글자 수 세기", "korean-character-count"],
  ["한국어 유행어 글쓰기", "korean-slang-writing"],
  ["K-스킬 클리너", "k-skill-cleaner"],
];



test("legacy blue ribbon package is not part of npm workspaces or pack dry run", () => {
  const packageJson = readJson("package.json");
  const packageLock = readJson("package-lock.json");
  const packScript = packageJson.scripts["pack:dry-run"];

  assert.doesNotMatch(packScript, /workspace blue-ribbon-nearby(?:\s|$)/);
  assert.ok(!fs.existsSync(path.join(repoRoot, "packages", "blue-ribbon-nearby", "package.json")));
  assert.ok(fs.existsSync(path.join(repoRoot, "legacy", "unsupported-packages", "blue-ribbon-nearby", "package.json")));
  assert.ok(!Object.hasOwn(packageLock.packages, "packages/blue-ribbon-nearby"));
  assert.ok(!Object.hasOwn(packageLock.packages, "node_modules/blue-ribbon-nearby"));
});

test("court auction Workflow C docs preserve the PGJ151 safety contract", () => {
  const featureDoc = read(path.join("docs", "features", "court-auction-notice-search.md"));

  assert.match(
    featureDoc,
    /물건 자유 조건검색[\s\S]*PGJ151F00/,
    "Workflow C docs should name the PGJ151F00 warmup path for property search",
  );
  assert.match(
    featureDoc,
    /pageSize[\s\S]*`10`\/`20`\/`50`\/`100`/,
    "Workflow C docs should keep pageSize aligned with the observed PGJ151 dropdown values",
  );
  assert.doesNotMatch(
    featureDoc,
    /세션 cookie\([^\n]+\)는 `GET \/pgj\/index\.on\?w2xPath=\/pgj\/ui\/pgj100\/PGJ143M01\.xml&pgjId=143M01` 으로 사전에 한 번 받아둡니다\./,
    "Workflow C docs should not imply every endpoint warms up through PGJ143M01 only",
  );
});

test("court auction pending changeset does not publish stale fallback or pageSize guidance", () => {
  const changesetDir = path.join(repoRoot, ".changeset");
  if (!fs.existsSync(changesetDir)) return;

  const pendingCourtAuctionChangesets = fs
    .readdirSync(changesetDir)
    .filter((entry) => entry.endsWith(".md"))
    .map((entry) => read(path.join(".changeset", entry)))
    .filter((contents) => contents.includes('"court-auction-notice-search"') && contents.includes("searchProperties()"));

  for (const contents of pendingCourtAuctionChangesets) {
    assert.doesNotMatch(
      contents,
      /direct HTTP call returns `BLOCKED` or `UPSTREAM_ERROR` 400/,
      "Changeset must not tell users that confirmed BLOCKED/ipcheck=false auto-falls back by default",
    );
    assert.doesNotMatch(
      contents,
      /`pageSize` is capped at 100/,
      "Changeset must not describe pageSize as an arbitrary 1..100 cap",
    );
    assert.match(
      contents,
      /`UPSTREAM_ERROR` 400/,
      "Changeset should still document the raw-HTTP WAF-style 400 fallback path",
    );
    assert.match(
      contents,
      /`BLOCKED`[\s\S]*`fallbackOnBlocked:true`/,
      "Changeset should document that confirmed BLOCKED retry is explicit opt-in",
    );
    assert.match(
      contents,
      /`10`\/`20`\/`50`\/`100`/,
      "Changeset should document the exact PGJ151 pageSize allowlist",
    );
  }
});

test("building register public docs use standard PNU land-category digits", () => {
  const docs = [
    ["feature guide", read(path.join("docs", "features", "building-register-search.md"))],
    ["proxy feature guide", read(path.join("docs", "features", "k-skill-proxy.md"))],
    ["proxy package README", read(path.join("packages", "k-skill-proxy", "README.md"))],
  ];

  for (const [label, doc] of docs) {
    assert.doesNotMatch(doc, /1168010100001230004/, `${label} should not publish a PNU with land category 0`);
    assert.match(doc, /1168010100101230004/, `${label} should publish a valid normal-land PNU example`);
  }

  const featureGuide = docs[0][1];
  assert.match(featureGuide, /토지구분\(1\)/);
  assert.match(featureGuide, /`1`\(일반 토지\)[\s\S]*`platGbCd=0`/);
  assert.match(featureGuide, /`2`\(산\)[\s\S]*`platGbCd=1`/);
});
