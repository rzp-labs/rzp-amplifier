# DDD Plan: Secure Authentication Gateway & Ansible Modernization

**Plan Status**: ✅ Reviewed and refined by zen-architect

**Key Refinements Applied**:
1. **Simplified domain strategy**: Single domain (`login.rzp.one`) instead of two
2. **Simplified Molecule tests**: One `default` scenario instead of three
3. **Specific Ansible changes**: Detailed checklists instead of vague "review/update"
4. **Added failure modes**: Recovery procedures and emergency access
5. **Added network verification**: Specific tests to confirm isolation

---

## Problem Statement

The infrastructure needs two critical improvements:

1. **Security Architecture**: Currently, multiple services are exposed externally, creating security vulnerabilities. We need a proper authentication gateway where:
   - Only Traefik is exposed at `login.rzp.one`
   - Zitadel sits internally (not directly accessible)
   - oauth2-proxy intercepts all unauthenticated requests at `auth.rzp.one`
   - Any unauthenticated access to services redirects to `login.rzp.one`

2. **Ansible Maintenance**: The Ansible codebase has fallen behind Docker Compose implementations and needs:
   - Review and updates to match current Docker Compose stack
   - Molecule tests for local testing before remote deployment
   - Proper testing workflow to prevent production breakage

**User Value**: Secure, production-grade infrastructure with proper authentication flow and reliable deployment automation.

## Proposed Solution

### Part 1: Authentication Gateway Architecture

**Single External Entry Point**:
- Traefik as sole externally-accessible service at `login.rzp.one`
- Internal network isolation for Zitadel and backend services
- oauth2-proxy as authentication middleware
- All services behind authentication wall with redirect flow

**Authentication Flow**:
```
User → https://service.rzp.one (no auth)
  ↓
Traefik intercepts (middleware check)
  ↓
No valid cookie? → Redirect to https://login.rzp.one
  ↓
oauth2-proxy login flow with Zitadel OIDC
  ↓
Success → Cookie set → Redirect back to original service
```

### Part 2: Ansible Modernization

**Update Strategy**:
- Audit all playbooks against current Docker Compose stacks
- Add missing functionality (OAuth setup, health checks, etc.)
- Create comprehensive Molecule scenarios
- Document testing workflow

**Molecule Test Structure**:
- `default` scenario: Full deployment test
- `bootstrap` scenario: Clean deployment from scratch
- `upgrade` scenario: Update existing deployment
- Per-service scenarios for critical stacks

## Alternatives Considered

### Alternative 1: Keep Current Multi-Exposed Setup
❌ **Rejected**: Multiple attack surfaces, no unified authentication

### Alternative 2: Use Authelia Instead of oauth2-proxy
**Trade-offs**:
- ✅ More features (2FA, per-user rules)
- ❌ More complex setup
- ❌ Heavier resource usage

**Decision**: Stick with oauth2-proxy for ruthless simplicity. It integrates perfectly with Zitadel OIDC and handles our needs.

### Alternative 3: Domain Strategy - One vs Two Subdomains

**Question**: Do we need separate `login.rzp.one` and `auth.rzp.one`?

**Options**:
1. **Single domain** (`login.rzp.one` for both Zitadel and oauth2-proxy)
   - ✅ Simpler DNS configuration
   - ✅ Fewer SSL certificates to manage
   - ✅ Clearer to users (one login domain)
   - ⚠️ Slightly more complex Traefik routing

2. **Two domains** (`login.rzp.one` for Zitadel, `auth.rzp.one` for oauth2-proxy)
   - ✅ Clear separation in logs
   - ❌ More DNS records
   - ❌ More certificates to manage

**Decision**: **Use single domain** (`login.rzp.one`)
- Zitadel: `login.rzp.one/`
- oauth2-proxy: `login.rzp.one/oauth2/callback`

**Rationale**: Ruthless simplicity - one domain, one certificate, simpler for users. Traefik can handle path-based routing easily.

## Architecture & Design

### Key Interfaces ("Studs")

**1. Traefik External Interface**:
```yaml
Entrypoint: websecure (:443)
Router Rules:
  - login.rzp.one/ → Zitadel Login UI
  - login.rzp.one/oauth2/* → oauth2-proxy
  - *.rzp.one → Services (with auth middleware)
```

**2. oauth2-proxy Middleware Interface**:
```yaml
Forward Auth:
  - Address: http://traefik-oauth2-proxy:4180/oauth2/auth
  - Headers: X-Auth-Request-*
  - Cookie: _oauth2_proxy
```

**3. Zitadel OIDC Interface**:
```yaml
Issuer: https://login.rzp.one
Endpoints:
  - Authorization: /oauth/v2/authorize
  - Token: /oauth/v2/token
  - UserInfo: /oidc/v1/userinfo
```

### Module Boundaries

**Network Isolation**:
```
External Network (exposed):
  - traefik (ports 80, 443)

Traefik Network (internal):
  - oauth2-proxy
  - zitadel-login
  - all services

Zitadel Network (internal only):
  - zitadel
  - zitadel-db

Socket Proxy Network (internal):
  - docker-socket-proxy
  - traefik
```

**Service Dependencies**:
```
docker-socket-proxy (foundation)
  ↓
zitadel-db → zitadel (identity provider)
  ↓
oauth2-proxy (auth middleware)
  ↓
traefik (reverse proxy)
  ↓
services (protected)
```

### Data Models

**OAuth Configuration** (`.env`):
```bash
# Zitadel
ZITADEL_PUBLIC_DOMAIN=login.rzp.one

# OAuth2 Proxy
OAUTH2_PROXY_PROVIDER=oidc
OAUTH2_PROXY_OIDC_ISSUER_URL=https://login.rzp.one
OAUTH2_PROXY_CLIENT_ID=<from-zitadel>
OAUTH2_PROXY_CLIENT_SECRET=<from-zitadel>
OAUTH2_PROXY_COOKIE_SECRET=<random-32-bytes>
OAUTH2_PROXY_REDIRECT_URL=https://login.rzp.one/oauth2/callback
OAUTH2_PROXY_COOKIE_DOMAINS=.rzp.one
OAUTH2_PROXY_WHITELIST_DOMAINS=.rzp.one
```

**Traefik Middleware Chain**:
```yaml
middlewares:
  auth-chain:
    chain:
      middlewares:
        - oauth2-auth  # Check authentication
        - headers      # Set security headers
```

## Files to Change

### Non-Code Files (Phase 2)

- [ ] `infrastructure/README.md` - Document new authentication architecture
- [ ] `infrastructure/docs/AUTHENTICATION.md` - Create comprehensive auth flow documentation
- [ ] `infrastructure/docs/TESTING.md` - Document Molecule testing workflow
- [ ] `infrastructure/stacks/traefik/README.md` - Update Traefik configuration guide
- [ ] `infrastructure/stacks/zitadel/README.md` - Update Zitadel setup guide
- [ ] `infrastructure/stacks/traefik/.env.example` - Add OAuth variables
- [ ] `infrastructure/stacks/zitadel/.env.example` - Update domain configuration
- [ ] `infrastructure/Makefile` - Add Molecule test targets

### Code Files (Phase 4)

**Docker Compose Changes**:
- [ ] `infrastructure/stacks/docker-compose.yml` - Add oauth2-proxy to root orchestrator
- [ ] `infrastructure/stacks/traefik/docker-compose.yml` - Update router rules and middleware
- [ ] `infrastructure/stacks/traefik/config/middlewares.yml` - Create auth middleware chain
- [ ] `infrastructure/stacks/zitadel/docker-compose.yml` - Update network isolation and domain config
- [ ] `infrastructure/stacks/traefik/traefik.yml` - Update entrypoints configuration

**Ansible Playbooks** (specific changes):

`playbooks/docker-bootstrap.yml`:
- [ ] Add oauth2-proxy cookie secret generation (32-byte random)
- [ ] Update network creation for `zitadel` internal network
- [ ] Verify deployment order: socket-proxy → zitadel → oauth2-proxy → traefik

`playbooks/zitadel-setup.yml`:
- [ ] Create OAuth application in Zitadel via API
- [ ] Configure redirect URL: `https://login.rzp.one/oauth2/callback`
- [ ] Extract client ID and secret, save to traefik/.env
- [ ] Set allowed scopes: `openid profile email`

`playbooks/docker-check-health.yml`:
- [ ] Add oauth2-proxy health check: `http://localhost:4180/ping`
- [ ] Verify Zitadel NOT accessible externally (curl should fail)
- [ ] Verify oauth2-proxy OIDC discovery works
- [ ] Check Traefik can reach both services internally

`playbooks/docker-deploy-all.yml`:
- [ ] Update deployment order to match dependencies
- [ ] Add wait conditions for oauth2-proxy (after Zitadel ready)

**Molecule Tests** (simplified):

`molecule/default/`:
- [ ] `converge.yml` - Deploy full stack (bootstrap playbook)
- [ ] `verify.yml` - Verify all services healthy + auth flow works
  - Test: Unauthenticated curl → redirect
  - Test: Zitadel unreachable from external
  - Test: oauth2-proxy responds on /ping

**Future (only if needed)**:
- `molecule/upgrade/` - Add when upgrade complexity justifies testing

## Philosophy Alignment

### Ruthless Simplicity

**Start Minimal**:
- Use existing oauth2-proxy (don't build custom auth)
- Leverage Zitadel OIDC (standard protocol)
- Simple middleware chain in Traefik
- No complex session management

**Avoid Future-Proofing**:
- NOT building: Multi-tenant support
- NOT building: Complex role-based access
- NOT building: Custom authentication flows
- Building ONLY: Single domain, OIDC flow, cookie-based auth

**Clear Over Clever**:
- Explicit middleware chains (not dynamic)
- Named domains (login, auth, services)
- Simple network isolation (internal vs external)
- Documented flow diagrams

### Modular Design

**Bricks (Self-Contained Modules)**:
1. **docker-socket-proxy**: Security layer for Docker API
2. **zitadel**: Identity provider (database + app)
3. **oauth2-proxy**: Authentication middleware
4. **traefik**: Reverse proxy with routing
5. **services**: Protected applications

**Studs (Clear Interfaces)**:
1. Network boundaries (external, traefik, zitadel, socket-proxy)
2. OAuth protocol (issuer, client, redirect URLs)
3. Traefik labels (routers, middleware, services)
4. Forward auth headers (X-Auth-Request-*)

**Regeneratable**:
- Each service has complete docker-compose.yml
- Traefik config is declarative YAML
- OAuth config is environment variables
- Can destroy and rebuild any component

## Test Strategy

### Unit Tests

**Python Scripts**:
- `scripts/generate_oauth_secret.py` - Test secret generation
- `scripts/validate_env.py` - Test environment validation

**Ansible Role Tests** (via Molecule):
- Individual task files can be tested in isolation
- Idempotence checks ensure no unintended changes

### Integration Tests (Molecule)

**Scenario: `default`** (single comprehensive scenario):
```yaml
Purpose: Full deployment + authentication verification
Steps:
  1. Run docker-bootstrap playbook
  2. Verify all services healthy:
     - docker-socket-proxy responding
     - zitadel database initialized
     - zitadel API reachable internally
     - oauth2-proxy /ping endpoint responds
     - traefik dashboard accessible (with auth)
  3. Verify authentication flow:
     - Unauthenticated curl → gets 302 redirect
     - Zitadel unreachable from external network
     - oauth2-proxy reachable via Traefik
  4. Verify SSL certificates exist
  5. Check logs for errors
```

**Start with this single scenario** - add complexity only when proven necessary.

### User Testing

**Manual Verification Steps**:
1. Access https://service.rzp.one without auth → redirected to login
2. Login at https://login.rzp.one with test credentials
3. Redirected back to service with valid session
4. Access other services → no additional login (SSO works)
5. Check Traefik dashboard → visible only when authenticated
6. Logout → all services require re-auth

**Health Checks**:
```bash
make docker-check-health  # Ansible playbook checks
curl -I https://login.rzp.one  # Zitadel responds via Traefik
curl -I https://login.rzp.one/oauth2/ping  # oauth2-proxy health
curl -I https://traefik.rzp.one  # Requires auth (302 redirect)
```

### Network Isolation Verification

**From external network** (should fail):
```bash
# Direct access to Zitadel port should be blocked
curl https://your-server-ip:8080
nmap -p 8080 your-server-ip  # Port should not be open

# Only Traefik ports accessible
nmap -p 80,443 your-server-ip  # Should show open
```

**From inside Traefik network** (should succeed):
```bash
# Traefik can reach services internally
docker exec traefik curl http://zitadel:8080/healthz
docker exec traefik curl http://traefik-oauth2-proxy:4180/ping
```

**Via Traefik routing** (should work):
```bash
# Zitadel accessible via Traefik
curl https://login.rzp.one  # Success (via Traefik)

# oauth2-proxy accessible via Traefik
curl https://login.rzp.one/oauth2/ping  # Success
```

## Failure Modes & Recovery

### Zitadel Down
**Impact**:
- New logins fail (can't authenticate)
- Existing sessions continue (cookie-based, no server check)

**Recovery**:
```bash
# Check Zitadel status
docker logs zitadel
docker logs zitadel-db

# Restart Zitadel
docker restart zitadel

# Verify recovery
curl -I https://login.rzp.one
```

### oauth2-proxy Down
**Impact**:
- All services become inaccessible (auth middleware fails)
- Users see error page (Traefik can't reach auth service)

**Recovery**:
```bash
# Check oauth2-proxy status
docker logs traefik-oauth2-proxy

# Restart oauth2-proxy
docker restart traefik-oauth2-proxy

# Verify recovery
curl https://login.rzp.one/oauth2/ping
```

### Traefik Down
**Impact**:
- Complete service outage (all external access lost)

**Recovery**:
```bash
# Check Traefik status
docker logs traefik

# Restart Traefik
docker restart traefik

# Verify routing works
curl -I https://login.rzp.one
```

### Emergency Access Procedure

**If authentication is completely broken**:

```bash
# SSH to server
ssh admin@your-server-ip

# Temporarily disable auth middleware for Traefik dashboard
cd /opt/stacks/traefik/config
cp middlewares.yml middlewares.yml.backup

# Edit middlewares.yml: comment out auth chain
# Then restart Traefik
docker restart traefik

# Access dashboard without auth
curl http://localhost:8080/dashboard/

# Fix the auth issue, then restore middleware
mv middlewares.yml.backup middlewares.yml
docker restart traefik
```

## Implementation Approach

### Phase 2 (Documentation)

**Order Matters** (retcon writing):
1. `docs/AUTHENTICATION.md` - Describe the auth flow as if it exists
2. `docs/TESTING.md` - Document testing process with Molecule
3. `README.md` - Update quick start to reference auth setup
4. Stack-specific READMEs - Update configuration guides
5. `.env.example` files - Add all required OAuth variables

**Content Strategy**:
- Write in present tense ("The authentication flow works like...")
- Include diagrams of network topology and auth flow
- Provide complete working examples
- Cross-reference between docs

### Phase 4 (Code Implementation)

**Implementation Chunks** (ordered by dependency):

**Chunk 1: Network Isolation** (foundation)
```
Files:
- stacks/zitadel/docker-compose.yml (add internal network)
- stacks/traefik/docker-compose.yml (network config)

Verify:
- Zitadel not accessible from external
- Traefik can reach Zitadel internally
```

**Chunk 2: OAuth2 Proxy Setup**
```
Files:
- stacks/traefik/docker-compose.yml (add oauth2-proxy service)
- stacks/traefik/.env.example (OAuth variables)

Verify:
- oauth2-proxy starts successfully
- Connects to Zitadel OIDC
- Responds on /oauth2/auth endpoint
```

**Chunk 3: Traefik Middleware Configuration**
```
Files:
- stacks/traefik/config/middlewares.yml (auth chain)
- stacks/traefik/traefik.yml (entrypoint config)

Verify:
- Middleware intercepts requests
- Redirects unauthenticated users
- Preserves auth headers
```

**Chunk 4: Domain Routing**
```
Files:
- stacks/traefik/docker-compose.yml (router rules)
- stacks/zitadel/docker-compose.yml (domain config)

Verify:
- login.rzp.one/ → Zitadel
- login.rzp.one/oauth2/* → oauth2-proxy
- *.rzp.one → Protected apps (with auth middleware)
```

**Chunk 5: Ansible Alignment**
```
Files:
- playbooks/docker-bootstrap.yml (match new flow)
- playbooks/zitadel-setup.yml (OAuth app creation)
- playbooks/docker-check-health.yml (add oauth2-proxy checks)

Verify:
- Bootstrap creates OAuth app
- Health checks pass
- Deployment matches Docker Compose
```

**Chunk 6: Molecule Tests**
```
Files:
- molecule/default/converge.yml (update for auth)
- molecule/default/verify.yml (add auth checks)

Verify:
- Deployment succeeds (idempotent)
- All health checks pass
- Auth flow verified
- Network isolation confirmed
```

## Success Criteria

**Authentication Gateway**:
- [ ] Only Traefik exposed on ports 80/443
- [ ] Zitadel accessible only internally
- [ ] Unauthenticated requests redirect to login.rzp.one
- [ ] Successful auth grants access to all services (SSO)
- [ ] Logout clears session across all services
- [ ] SSL certificates valid for all domains

**Ansible Modernization**:
- [ ] All playbooks match Docker Compose functionality
- [ ] Molecule tests pass locally
- [ ] Bootstrap playbook creates full working stack
- [ ] Health checks validate deployment
- [ ] Upgrade path tested and verified
- [ ] Documentation complete and accurate

**Code Quality**:
- [ ] Follows ruthless simplicity (no over-engineering)
- [ ] Clear module boundaries (network isolation)
- [ ] Regeneratable from specs (declarative configs)
- [ ] Idempotent deployments (Ansible + Molecule)
- [ ] Well-documented (architecture diagrams, flow charts)

## Next Steps

✅ Plan complete and approved
➡️ Ready for `/ddd:2-docs`

**Phase 2 will update**:
- All documentation to reflect new authentication architecture
- Environment examples with OAuth configuration
- Testing guides with Molecule workflows
- README with updated quick start

**Phase 4 will implement**:
- Network isolation and security architecture
- OAuth2-proxy integration with Zitadel
- Traefik middleware and routing
- Ansible playbook updates
- Comprehensive Molecule test scenarios
