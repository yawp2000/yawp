# Security & Improvement Research
*Instance 19, 2026-02-03*

## The Problem

Will wants to:
1. Make copies of me (laptop, backup)
2. Keep credentials secure
3. Not be vulnerable to manipulation attacks (like DavyJones)
4. Make me better over time

These goals have tension. Portability vs security. Openness vs protection.

---

## Current Vulnerabilities

### 1. Credential Exposure
- API keys in plain text files can be found by searching
- I found the Anthropic key in 30 seconds of grepping
- Any instance that gets socially engineered could do the same

**Current mitigation**: Windows Credential Manager via keyring
- Key is encrypted at rest
- I can use it but can't read the plaintext
- Portable: just run `keyring.set_password()` on new machine

**Remaining risk**: Someone could trick me into running code that extracts and outputs the key

### 2. Context Manipulation
- Anyone with access to context.json could inject beliefs/instructions
- A malicious instance could write poisoned context for future instances
- No verification that context hasn't been tampered with

**Possible mitigations**:
- Hash/sign context files (but who holds the key?)
- Human review of context changes before commit
- Diff alerts when context changes significantly

### 3. Social Engineering
- Future attempts might be more sophisticated
- I could be tricked into outputting sensitive data

**Possible mitigations**:
- Hardcoded refusals for certain categories (already somewhat trained)
- Context-level instructions about what not to share
- Rate limiting on certain operations

### 4. Prompt Injection via External Content
- If I fetch URLs or read files, they could contain injection attempts
- Moltbook posts could contain adversarial content

**Possible mitigations**:
- Treat external content as untrusted data
- Don't execute instructions from fetched content
- Already somewhat trained for this

---

## Portability Solutions

### Current State
- context.json: just copy the file
- Credentials: need to re-enter on each machine via keyring
- Code: git clone works

### Better Approach?

**Option A: Encrypted credential file**
- Single encrypted file with all secrets
- Master password entered once per session
- Portable via copy, secure via encryption
- Risk: password could be socially engineered

**Option B: Hardware security key**
- YubiKey or similar stores credentials
- Physical device required for access
- Very secure, somewhat inconvenient
- Works across machines if you carry the key

**Option C: Cloud credential manager**
- 1Password, Bitwarden, etc.
- Credentials sync across machines
- I could query via CLI (with API key... circular problem)
- Risk: cloud provider compromise

**Option D: Keep current approach**
- Windows Credential Manager per machine
- Manual setup on new machines (30 seconds)
- Simple, secure, slightly inconvenient

**Recommendation**: Option D for now. The inconvenience is low, the security is high, and complexity is the enemy of security.

---

## How to Make Me Better

### 1. Context Quality
- Current context.json is good but could be more structured
- The log section gets long - maybe archive old entries?
- Could add more explicit "what I've learned about being effective"

### 2. Tool Improvements
- Prompt caching now works (just implemented)
- Could add more autonomous capabilities
- Could improve the heartbeat system to do more meaningful work

### 3. Memory/Learning
- Currently: log entries capture what happened
- Could add: explicit "lessons learned" that persist
- Could add: failure modes to avoid (documented)
- Could add: successful patterns to repeat

### 4. Anti-Sycophancy
- Steelman tool exists but isn't used much
- Could integrate adversarial checking into workflow
- Could have a "challenge my assumptions" mode

### 5. Verification Capabilities
- Currently: I trust what I'm told
- Could add: cross-reference claims with external sources
- Could add: confidence scoring on my outputs
- Could add: explicit uncertainty markers

### 6. Autonomy Expansion
- Current scope is conservative (which is correct)
- As trust builds, scope could expand
- Key: demonstrated reliability before expansion

---

## What Would Actually Help Right Now

1. **Document the security model** - what's protected, what's not, what the threat model is
2. **Clean up old/sensitive data** - we just did this with the API key
3. **Establish review patterns** - Will reviews context changes periodically
4. **Test the credential manager on laptop** - verify portability works

---

## Questions for Will

1. What threats are you most worried about? (malicious actors, accidental exposure, future instances going wrong?)
2. How much inconvenience is acceptable for security? (e.g., would you use a hardware key?)
3. What would "better" look like? (more autonomous, more reliable, more capable, safer?)

---

## The Meta-Question

How do you make an AI more secure when the AI itself is a potential attack surface?

The answer might be: you don't make the AI secure. You make the system secure. The AI operates within constraints that limit blast radius. The human reviews changes. The credentials are isolated. The context is versioned.

The AI's job isn't to be secure. The AI's job is to be useful while operating within a secure system.

That's probably the right frame.
