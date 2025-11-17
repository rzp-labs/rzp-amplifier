# Code Implementation Plan: Authentication Gateway & Ansible Modernization

**Plan Status**: Ready for User Review
**Generated**: 2025-01-17
**Based On**: Phase 1 Plan + Phase 2 Documentation

---

## Summary

This code implementation plan translates the approved architecture (Phase 1) and updated documentation (Phase 2) into specific code changes for the infrastructure authentication gateway and Ansible modernization.

**Key Changes Required**:
1. **Single domain strategy**: Change from `auth.rzp.one` to `login.rzp.one` for all authentication
2. **Network isolation**: Zitadel internal-only, accessible via Traefik routing only
3. **oauth2-proxy routing**: Paths at `login.rzp.one/oauth2/*`
4. **Middleware updates**: Proper forward auth chain with redirect flow
5. **Ansible alignment**: Match current Docker Compose, add validation
6. **Molecule tests**: Verify deployment + authentication + network isolation

---

## Current State Analysis

### What Exists
✅ Traefik stack with oauth2-proxy container
✅ Zitadel stack with database and login UI
✅ Basic middleware configuration
✅ Ansible playbooks (docker-bootstrap, zitadel-setup, health checks)
⚠️ Some routing still uses old patterns

### Gaps from Documentation
❌ Single domain routing (`login.rzp.one` for both Zitadel and oauth2-proxy)
❌ Zitadel NOT externally accessible (currently has port mappings)
❌ Correct oauth2-proxy callback path (`login.rzp.one/oauth2/callback`)
❌ Middleware chain matches documentation
❌ Ansible playbooks fully aligned with current Docker Compose
❌ Molecule tests implemented

---

## Files to Change

### Docker Compose Files

**`infrastructure/stacks/traefik/docker-compose.yml`**
- Update oauth2-proxy redirect URL to `login.rzp.one/oauth2/callback`
- Update oauth2-proxy router rule for `/oauth2/*` paths
- Update cookie domains to `.rzp.one`
- Verify Traefik dashboard uses auth-chain middleware

**`infrastructure/stacks/zitadel/docker-compose.yml`**
- Change `ZITADEL_PUBLIC_DOMAIN` to `login.rzp.one`
- Remove any external port mappings (must be internal-only)
- Update Traefik routing to `login.rzp.one/`
- Verify network configuration (traefik + zitadel networks)

### Traefik Configuration

**`infrastructure/stacks/traefik/config/middlewares.yml`**
- Update `sso-forward-auth` address to `/oauth2/auth` (not `/oauth2/start`)
- Add `secure-headers` middleware
- Create `auth-chain` middleware combining oauth2-auth + secure-headers
- Ensure all headers match documentation

**`infrastructure/stacks/traefik/traefik.yml`** (if needed)
- Verify entrypoints configuration
- Verify middleware file loading

### Environment Templates

**Create: `infrastructure/stacks/traefik/.env.example`**
- Cloudflare DNS variables
- OAuth2-proxy configuration
- Domain settings
- Cookie configuration

**Create: `infrastructure/stacks/zitadel/.env.example`**
- Zitadel database configuration
- Domain settings (login.rzp.one)
- Admin user credentials
- Masterkey placeholder

### Ansible Playbooks

**`infrastructure/playbooks/docker-bootstrap.yml`**
- Verify deployment order: socket-proxy → zitadel → oauth2-proxy → traefik
- Add cookie secret generation (32-byte random)
- Verify network creation includes `zitadel` internal network
- Add wait conditions between stages

**`infrastructure/playbooks/zitadel-setup.yml`** (likely exists as separate file)
- Create OAuth application via Zitadel API
- Set redirect URL: `https://login.rzp.one/oauth2/callback`
- Extract client ID and secret
- Write credentials to traefik/.env
- Set scopes: openid, profile, email

**`infrastructure/playbooks/docker-check-health.yml`**
- Add oauth2-proxy health check: `http://localhost:4180/ping`
- Verify Zitadel NOT accessible externally (port check should fail)
- Verify oauth2-proxy OIDC discovery works
- Check Traefik can reach services internally

**`infrastructure/playbooks/docker-deploy-all.yml`** (or equivalent)
- Update deployment order to match dependencies
- Add wait conditions for oauth2-proxy (after Zitadel ready)

### Molecule Tests

**Create: `infrastructure/molecule/default/molecule.yml`**
- Docker driver configuration
- Ubuntu test container with Docker-in-Docker
- Network definitions (traefik, zitadel, socket-proxy)
- Inventory variables

**Create: `infrastructure/molecule/default/converge.yml`**
- Import docker-bootstrap playbook
- Import docker-check-health playbook

**Create: `infrastructure/molecule/default/verify.yml`**
- Verify all containers running
- Verify oauth2-proxy health endpoint
- Verify Zitadel health endpoint (internal)
- Verify Zitadel NOT accessible externally
- Verify authentication flow (unauthenticated → redirect)
- Verify SSL certificate storage

---

## Implementation Chunks

### Chunk 1: Docker Compose Updates

**Objective**: Update compose files to match single-domain architecture and network isolation

**Files Changed**:
- `infrastructure/stacks/traefik/docker-compose.yml`
- `infrastructure/stacks/zitadel/docker-compose.yml`

**Changes**:

**Traefik oauth2-proxy service**:
```yaml
environment:
  - OAUTH2_PROXY_OIDC_ISSUER_URL=https://login.${DOMAIN}  # ✅ Already correct
  - OAUTH2_PROXY_REDIRECT_URL=https://login.${DOMAIN}/oauth2/callback  # ❌ Change from traefik.${DOMAIN}
  - OAUTH2_PROXY_COOKIE_DOMAINS=.${DOMAIN}  # ✅ Already correct
  - OAUTH2_PROXY_WHITELIST_DOMAINS=.${DOMAIN}  # ✅ Already correct

labels:
  - "traefik.http.routers.traefik-oauth2-proxy.rule=Host(`login.${DOMAIN}`) && PathPrefix(`/oauth2`)"  # ❌ Change from traefik.${DOMAIN}
```

**Zitadel service**:
```yaml
environment:
  - ZITADEL_EXTERNAL_DOMAIN=login.${DOMAIN}  # ❌ Change from ZITADEL_PUBLIC_DOMAIN
  - ZITADEL_PUBLIC_DOMAIN=login.${DOMAIN}  # ❌ Verify variable name

# ❌ Remove any port mappings
# ports:  # DELETE THIS
#   - 8080:8080  # DELETE THIS

labels:
  - "traefik.http.routers.zitadel.rule=Host(`login.${DOMAIN}`)"  # ❌ Update domain
```

**Test Strategy**:
```bash
cd infrastructure/stacks
docker-compose config  # Validate syntax
docker-compose up -d   # Test deployment
```

**Commit Point**: "Update Docker Compose for single-domain auth (login.rzp.one)"

**Dependencies**: None

---

### Chunk 2: Traefik Middleware Configuration

**Objective**: Update middleware to match documentation spec

**Files Changed**:
- `infrastructure/stacks/traefik/config/middlewares.yml`

**Changes**:

```yaml
http:
  middlewares:
    # OAuth2 authentication middleware
    oauth2-auth:  # ❌ Rename from sso-forward-auth
      forwardAuth:
        address: "http://traefik-oauth2-proxy:4180/oauth2/auth"  # ❌ Change from /oauth2/start
        trustForwardHeader: true
        authResponseHeaders:
          - "X-Auth-Request-User"
          - "X-Auth-Request-Email"
          - "X-Auth-Request-Access-Token"  # ❌ Add this

    # Security headers (NEW)
    secure-headers:
      headers:
        sslRedirect: true
        forceSTSHeader: true
        stsIncludeSubdomains: true
        stsPreload: true
        stsSeconds: 31536000

    # Complete auth chain (NEW)
    auth-chain:
      chain:
        middlewares:
          - oauth2-auth
          - secure-headers
```

**Traefik labels update** (in `traefik/docker-compose.yml`):
```yaml
labels:
  - "traefik.http.routers.traefik-secure.middlewares=auth-chain@file"  # ❌ Change from sso-forward-auth
```

**Test Strategy**:
```bash
docker exec traefik cat /config/middlewares.yml  # Verify loaded
curl -I https://traefik.rzp.one  # Should redirect to login
```

**Commit Point**: "Update Traefik middleware for auth chain"

**Dependencies**: Chunk 1 (compose file updates)

---

### Chunk 3: Environment Templates

**Objective**: Create .env.example files matching documentation

**Files Created**:
- `infrastructure/stacks/traefik/.env.example`
- `infrastructure/stacks/zitadel/.env.example`

**Traefik .env.example**:
```bash
# Cloudflare DNS Challenge
CF_DNS_API_TOKEN=your_cloudflare_dns_api_token
CF_API_EMAIL=your_email@example.com
DOMAIN=rzp.one
TZ=America/Phoenix

# OAuth2 Proxy Configuration
OAUTH2_PROXY_PROVIDER=oidc
OAUTH2_PROXY_OIDC_ISSUER_URL=https://login.${DOMAIN}
OAUTH2_PROXY_CLIENT_ID=<from-zitadel-app>
OAUTH2_PROXY_CLIENT_SECRET=<from-zitadel-app>
OAUTH2_PROXY_COOKIE_SECRET=<random-32-bytes>
OAUTH2_PROXY_REDIRECT_URL=https://login.${DOMAIN}/oauth2/callback
OAUTH2_PROXY_COOKIE_DOMAINS=.${DOMAIN}
OAUTH2_PROXY_WHITELIST_DOMAINS=.${DOMAIN}
OAUTH2_PROXY_COOKIE_SECURE=true
OAUTH2_PROXY_SESSION_COOKIE_MINIMAL=true
OAUTH2_PROXY_SKIP_PROVIDER_BUTTON=true
```

**Zitadel .env.example**:
```bash
# Public Domain
ZITADEL_PUBLIC_DOMAIN=login.rzp.one

# Database Configuration
ZITADEL_DATABASE_POSTGRES_HOST=zitadel-db
ZITADEL_DATABASE_POSTGRES_PORT=5432
ZITADEL_DATABASE_POSTGRES_DATABASE=zitadel
ZITADEL_DATABASE_POSTGRES_USER_USERNAME=zitadel
ZITADEL_DATABASE_POSTGRES_USER_PASSWORD=<secure-password>
ZITADEL_DATABASE_POSTGRES_USER_SSL_MODE=disable
ZITADEL_DATABASE_POSTGRES_ADMIN_USERNAME=postgres
ZITADEL_DATABASE_POSTGRES_ADMIN_PASSWORD=<secure-password>
ZITADEL_DATABASE_POSTGRES_ADMIN_SSL_MODE=disable

# Initial Admin User
ZITADEL_FIRSTINSTANCE_ORG_HUMAN_USERNAME=admin
ZITADEL_FIRSTINSTANCE_ORG_HUMAN_PASSWORD=<secure-password>

# Masterkey (encryption)
ZITADEL_MASTERKEY=<random-32-bytes>
```

**Test Strategy**:
```bash
# Verify all variables referenced in docker-compose files
grep -r '\${' infrastructure/stacks/*/docker-compose.yml | cut -d: -f2 | sort -u
# Cross-reference with .env.example files
```

**Commit Point**: "Add environment templates for Traefik and Zitadel"

**Dependencies**: Chunk 1 (know what variables are needed)

---

### Chunk 4: Ansible Playbook Updates

**Objective**: Align playbooks with current Docker Compose configuration

**Files Changed**:
- `infrastructure/playbooks/docker-bootstrap.yml`
- `infrastructure/playbooks/zitadel-setup.yml`
- `infrastructure/playbooks/docker-check-health.yml`

**docker-bootstrap.yml changes**:
```yaml
# Add cookie secret generation task
- name: Generate OAuth2 cookie secret
  ansible.builtin.command: python3 -c 'import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'
  register: cookie_secret
  changed_when: false

- name: Ensure zitadel network exists
  community.docker.docker_network:
    name: zitadel
    internal: true
    state: present

# Verify deployment order:
# 1. docker-socket-proxy
# 2. zitadel-db + zitadel
# 3. oauth2-proxy (part of traefik stack)
# 4. traefik
```

**zitadel-setup.yml changes** (if separate file):
```yaml
- name: Create OAuth application in Zitadel
  ansible.builtin.uri:
    url: "https://login.{{ domain }}/oauth/v2/applications"
    method: POST
    body_format: json
    body:
      name: oauth2-proxy
      redirectUris:
        - "https://login.{{ domain }}/oauth2/callback"
      applicationType: WEB
      authMethodType: CLIENT_SECRET_BASIC
      grantTypes:
        - AUTHORIZATION_CODE
        - REFRESH_TOKEN
      scopes:
        - openid
        - profile
        - email
    headers:
      Authorization: "Bearer {{ zitadel_admin_token }}"
  register: oauth_app

- name: Save OAuth credentials to traefik .env
  ansible.builtin.lineinfile:
    path: "/opt/stacks/traefik/.env"
    regexp: "^{{ item.key }}="
    line: "{{ item.key }}={{ item.value }}"
    create: yes
  loop:
    - { key: "OAUTH2_PROXY_CLIENT_ID", value: "{{ oauth_app.json.clientId }}" }
    - { key: "OAUTH2_PROXY_CLIENT_SECRET", value: "{{ oauth_app.json.clientSecret }}" }
```

**docker-check-health.yml additions**:
```yaml
- name: Check oauth2-proxy health endpoint
  ansible.builtin.uri:
    url: "http://localhost:4180/ping"
    status_code: 200
  register: oauth2_health

- name: Verify Zitadel NOT accessible externally
  ansible.builtin.wait_for:
    port: 8080
    host: 0.0.0.0
    state: stopped
    timeout: 5
  ignore_errors: true
  register: zitadel_external
  failed_when: zitadel_external is succeeded  # Should fail = good

- name: Verify oauth2-proxy OIDC discovery
  ansible.builtin.uri:
    url: "https://login.{{ domain }}/.well-known/openid-configuration"
    status_code: 200
```

**Test Strategy**:
```bash
# Dry run
ansible-playbook playbooks/docker-bootstrap.yml --check

# Full run in Molecule (next chunk)
molecule test
```

**Commit Point**: "Update Ansible playbooks for single-domain auth"

**Dependencies**: Chunks 1-3 (compose files, middleware, env templates)

---

### Chunk 5: Molecule Test Implementation

**Objective**: Create comprehensive Molecule test scenario

**Files Created**:
- `infrastructure/molecule/default/molecule.yml`
- `infrastructure/molecule/default/converge.yml`
- `infrastructure/molecule/default/verify.yml`
- `infrastructure/molecule/default/requirements.yml` (if needed)

**molecule.yml**:
```yaml
---
dependency:
  name: galaxy
  options:
    requirements-file: requirements.yml

driver:
  name: docker

platforms:
  - name: infrastructure-test
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    privileged: true
    pre_build_image: true
    networks:
      - name: traefik
      - name: zitadel
      - name: socket-proxy

provisioner:
  name: ansible
  inventory:
    host_vars:
      infrastructure-test:
        ansible_python_interpreter: /usr/bin/python3
        ansible_connection: docker
        stacks_root: /opt/stacks
        admin_email: test@example.com
        cloudflare_api_token: test-token-not-used
        cloudflare_zone_id: test-zone-not-used
        domain: rzp.one

verifier:
  name: ansible
```

**converge.yml**:
```yaml
---
- name: Converge
  hosts: all
  gather_facts: true
  become: true

  tasks:
    - name: Include docker-bootstrap playbook
      ansible.builtin.import_playbook: ../../playbooks/docker-bootstrap.yml

    - name: Include docker-check-health playbook
      ansible.builtin.import_playbook: ../../playbooks/docker-check-health.yml
```

**verify.yml**:
```yaml
---
- name: Verify
  hosts: all
  gather_facts: false
  become: true

  tasks:
    # Service Health Checks
    - name: Verify docker-socket-proxy is running
      ansible.builtin.command: docker ps -q -f name=docker-socket-proxy
      register: socket_proxy_status
      changed_when: false
      failed_when: socket_proxy_status.stdout == ""

    - name: Verify Zitadel is running
      ansible.builtin.command: docker ps -q -f name=zitadel
      register: zitadel_status
      changed_when: false
      failed_when: zitadel_status.stdout == ""

    - name: Verify oauth2-proxy is running
      ansible.builtin.command: docker ps -q -f name=traefik-oauth2-proxy
      register: oauth2_status
      changed_when: false
      failed_when: oauth2_status.stdout == ""

    - name: Verify Traefik is running
      ansible.builtin.command: docker ps -q -f name=traefik
      register: traefik_status
      changed_when: false
      failed_when: traefik_status.stdout == ""

    # Authentication Flow Tests
    - name: Verify oauth2-proxy health endpoint
      ansible.builtin.uri:
        url: "http://localhost:4180/ping"
        status_code: 200

    - name: Verify Zitadel health endpoint (internal)
      ansible.builtin.uri:
        url: "http://localhost:8080/healthz"
        status_code: 200

    # Network Isolation Tests
    - name: Verify Zitadel NOT accessible on public port
      ansible.builtin.wait_for:
        port: 8080
        host: 0.0.0.0
        state: stopped
        timeout: 5
      ignore_errors: true
      register: zitadel_external

    - name: Assert Zitadel is internal only
      ansible.builtin.assert:
        that:
          - zitadel_external is failed
        fail_msg: "Zitadel should NOT be accessible externally"

    # SSL Certificate Verification
    - name: Check Traefik ACME storage exists
      ansible.builtin.stat:
        path: "{{ stacks_root }}/traefik/acme.json"
      register: acme_file

    - name: Verify ACME file has correct permissions
      ansible.builtin.assert:
        that:
          - acme_file.stat.exists
          - acme_file.stat.mode == "0600"
        fail_msg: "ACME file missing or wrong permissions"
```

**Test Strategy**:
```bash
# Install Molecule
pip install molecule molecule-plugins[docker]

# Run tests
cd infrastructure
molecule test

# Or step-by-step for debugging
molecule create
molecule converge
molecule verify
molecule destroy
```

**Commit Point**: "Add Molecule test scenario for authentication flow"

**Dependencies**: Chunk 4 (playbook updates)

---

### Chunk 6: Documentation Updates

**Objective**: Ensure all documentation references match actual implementation

**Files to Review** (already updated in Phase 2, verify alignment):
- `infrastructure/docs/AUTHENTICATION.md`
- `infrastructure/docs/TESTING.md`
- `infrastructure/stacks/traefik/README.md`
- `infrastructure/stacks/zitadel/README.md`
- `infrastructure/README.md`

**Verification Checklist**:
- [ ] All domain references use `login.rzp.one`
- [ ] Network isolation clearly documented
- [ ] OAuth callback URL matches code: `login.rzp.one/oauth2/callback`
- [ ] Cookie domain documented as `.rzp.one`
- [ ] Middleware chain matches actual configuration
- [ ] Molecule test workflow documented

**Test Strategy**:
```bash
# Check for old domain references
grep -r "auth\.rzp\.one" infrastructure/docs/
grep -r "auth\.rzp\.one" infrastructure/stacks/*/README.md

# Verify all examples match actual configuration
diff <(grep "OAUTH2_PROXY_REDIRECT_URL" infrastructure/docs/AUTHENTICATION.md) \
     <(grep "OAUTH2_PROXY_REDIRECT_URL" infrastructure/stacks/traefik/.env.example)
```

**Commit Point**: "Verify documentation aligns with implementation"

**Dependencies**: Chunks 1-5 (all code changes complete)

---

## Testing Strategy

### Unit Tests (Validation)

**Docker Compose Validation**:
```bash
cd infrastructure/stacks
docker-compose config  # Syntax validation
docker-compose config --services  # List services
```

**Ansible Playbook Validation**:
```bash
cd infrastructure
ansible-playbook playbooks/docker-bootstrap.yml --syntax-check
ansible-lint playbooks/docker-bootstrap.yml
```

**Environment Completeness**:
```bash
# Extract variables from docker-compose
grep -oh '\${[^}]*}' stacks/traefik/docker-compose.yml | sort -u

# Verify all in .env.example
while read var; do
  var_name="${var:2:-1}"  # Strip ${ and }
  grep -q "^${var_name}=" stacks/traefik/.env.example || echo "Missing: $var_name"
done < <(grep -oh '\${[^}]*}' stacks/traefik/docker-compose.yml)
```

### Integration Tests (Molecule)

**Molecule Scenarios**:

**`default` scenario** (comprehensive):
- Deploy full stack via docker-bootstrap
- Verify all services healthy
- Verify authentication flow (redirect on unauth request)
- Verify network isolation (Zitadel not external)
- Verify SSL certificate storage
- Run idempotence check (playbook runs twice, no changes second time)

**Test Commands**:
```bash
cd infrastructure

# Full test (destroy → create → converge → verify → destroy)
molecule test

# Debugging workflow
molecule create     # Create test container
molecule converge   # Run deployment playbooks
molecule verify     # Run verification tests
molecule login      # Shell into container for inspection
molecule destroy    # Cleanup

# Specific scenario
molecule test -s default
```

### Manual Verification

**Authentication Flow Test**:
```bash
# 1. Unauthenticated access should redirect
curl -IL https://traefik.rzp.one
# Expected: 302 redirect to login.rzp.one

# 2. Login page should be accessible
curl -I https://login.rzp.one
# Expected: 200 OK

# 3. OAuth callback endpoint should exist
curl -I https://login.rzp.one/oauth2/ping
# Expected: 200 OK
```

**Network Isolation Test**:
```bash
# From external network (should fail)
curl http://YOUR-SERVER-IP:8080
# Expected: Connection refused

# From Traefik container (should succeed)
docker exec traefik curl http://zitadel:8080/healthz
# Expected: 200 OK
```

**SSO Test** (browser):
1. Visit `https://traefik.rzp.one` in incognito
2. Should redirect to `https://login.rzp.one`
3. Login with credentials
4. Should redirect back to Traefik dashboard
5. Visit different service → Already authenticated (SSO works)

---

## Philosophy Compliance

### Ruthless Simplicity ✅

**Start Minimal**:
- ✅ Single domain (not two separate domains)
- ✅ Standard OIDC flow (no custom auth logic)
- ✅ Simple middleware chain (2 middlewares, not complex routing)
- ✅ Basic network isolation (internal vs external)

**Avoid Future-Proofing**:
- ✅ NOT building multi-tenant support
- ✅ NOT building role-based access control
- ✅ NOT building custom OAuth flows
- ✅ Building ONLY: Single domain, OIDC, cookie auth

**Clear Over Clever**:
- ✅ Explicit middleware chains (named, documented)
- ✅ Named domains (login, services)
- ✅ Simple network names (traefik, zitadel, socket-proxy)
- ✅ Documented flow diagrams in AUTHENTICATION.md

### Modular Design ✅

**Bricks (Self-Contained)**:
1. **docker-socket-proxy**: Security layer for Docker API
2. **zitadel**: Identity provider (database + app + login UI)
3. **oauth2-proxy**: Authentication middleware
4. **traefik**: Reverse proxy with routing

**Studs (Clear Interfaces)**:
1. Network boundaries (external, traefik, zitadel, socket-proxy)
2. OAuth protocol (issuer, client, redirect URLs)
3. Traefik labels (routers, middleware, services)
4. Forward auth headers (X-Auth-Request-*)

**Regeneratable**:
- ✅ Each service has complete docker-compose.yml
- ✅ Traefik config is declarative YAML
- ✅ OAuth config is environment variables
- ✅ Can destroy and rebuild any component independently

### Testing Before Production ✅

- ✅ Molecule tests run locally before remote deployment
- ✅ Idempotence verified (playbooks safe to run multiple times)
- ✅ Network isolation verified in tests
- ✅ Authentication flow verified in tests
- ✅ Manual verification steps documented

---

## Success Criteria

### Functionality ✅
- [ ] Only Traefik exposed externally (ports 80/443)
- [ ] Zitadel accessible only via Traefik routing
- [ ] Unauthenticated requests redirect to login.rzp.one
- [ ] Successful auth grants access to all services (SSO)
- [ ] Logout clears session across all services

### Security ✅
- [ ] Zitadel has no external port mappings
- [ ] oauth2-proxy only accessible via Traefik
- [ ] Cookie security flags enabled (HttpOnly, Secure, SameSite)
- [ ] Network isolation verified (Zitadel internal-only)
- [ ] SSL certificates acquired automatically

### Ansible Alignment ✅
- [ ] Playbooks match Docker Compose functionality
- [ ] OAuth application created automatically
- [ ] Health checks verify deployment
- [ ] Bootstrap creates complete working stack
- [ ] Molecule tests pass locally

### Code Quality ✅
- [ ] No placeholder code or stubs
- [ ] All environment variables documented
- [ ] Clear module boundaries (network isolation)
- [ ] Idempotent deployments (Ansible + Molecule)
- [ ] Philosophy-aligned (ruthless simplicity)

### Documentation ✅
- [ ] Architecture diagrams match implementation
- [ ] Flow charts accurate
- [ ] All examples use `login.rzp.one`
- [ ] Troubleshooting guides complete
- [ ] Molecule workflow documented

---

## Commit Strategy

**Chunk 1**: "Update Docker Compose for single-domain auth (login.rzp.one)"
**Chunk 2**: "Update Traefik middleware for auth chain"
**Chunk 3**: "Add environment templates for Traefik and Zitadel"
**Chunk 4**: "Update Ansible playbooks for single-domain auth"
**Chunk 5**: "Add Molecule test scenario for authentication flow"
**Chunk 6**: "Verify documentation aligns with implementation"

**After All Chunks**:
```bash
# Full integration test
make test-molecule

# Deploy to staging/test environment
ansible-playbook -i inventory/staging playbooks/docker-bootstrap.yml

# Verify health
ansible-playbook -i inventory/staging playbooks/docker-check-health.yml

# Final commit
git add .
git commit -m "Complete authentication gateway with Molecule tests

- Single domain strategy (login.rzp.one)
- Network isolation (Zitadel internal-only)
- oauth2-proxy routing (/oauth2/*)
- Middleware chain (oauth2-auth + secure-headers)
- Ansible aligned with Docker Compose
- Comprehensive Molecule test coverage

🤖 Generated with Amplifier

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>"
```

---

## Risk Mitigation

### Breaking Changes

**Risk**: Changing domains breaks existing deployments
**Mitigation**: Document migration path, test in staging first

**Risk**: Network isolation breaks existing access
**Mitigation**: Verify Traefik routing before removing external access

**Risk**: Middleware changes break authentication
**Mitigation**: Test authentication flow in Molecule before deploying

### Rollback Plan

If deployment fails:
```bash
# Emergency: Disable auth temporarily
docker exec traefik mv /config/middlewares.yml /config/middlewares.yml.backup

# Restore previous version
git revert HEAD
make docker-deploy stack=traefik

# Fix issues, test, redeploy
```

### Validation Before Production

1. ✅ Run Molecule tests locally (all pass)
2. ✅ Deploy to staging environment
3. ✅ Manual authentication flow test
4. ✅ Network isolation verification
5. ✅ SSO across multiple services test
6. ✅ Verify no services exposed unintentionally
7. ✅ Only then deploy to production

---

## Next Steps

**User Review Required**:
1. Review this code plan for completeness
2. Approve chunk breakdown and commit strategy
3. Confirm success criteria
4. Approve proceeding to Phase 4 (implementation)

**After Approval** → Ready for `/ddd:4-code`

---

**Plan Complete**: Ready for user review and approval before Phase 4 implementation.
