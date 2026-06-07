# Hackathon Workflow Guide (6-8 Hours)

## Hour 0: Setup (30 min)

```bash
cp .env.example .env
# Add OPENAI_API_KEY or OPENROUTER_API_KEY
make install
make backend   # terminal 1
make frontend  # terminal 2
```

Verify: http://localhost:3000 and http://localhost:8000/docs

## Hour 1: Pick Idea (30 min)

Read `examples/` folder. Pick ONE:
- **Fastest demo**: Multi-Agent Network (workflow already works)
- **Best blockchain story**: Agent Marketplace + Reputation
- **Most impressive**: AI Wallet Assistant

Fill out `pitch/final_submission_template.md` with your choice.

## Hour 2-3: Core Feature (2 hours)

| Idea | Focus |
|------|-------|
| Marketplace | Customize AgentCard data, add hire button |
| Freelancer | Tune prompts, improve workflow output |
| Reputation | Deploy contract from monad/smart_contract_notes.md |
| Wallet | Wire wallet_agent to ethers.js |
| Multi-agent | Upgrade workflow.py to LangGraph |

## Hour 4-5: Blockchain Layer (2 hours)

1. Get testnet MON from faucet
2. Create agent wallet (monad/wallet_examples.md)
3. Deploy minimal contract OR show signed message
4. Display tx hash in DemoPanel or WalletCard

## Hour 5-6: Polish UI (1 hour)

- Customize landing page hero text
- Add your project name to Navbar
- Ensure /demo workflow runs smoothly
- Test chat on agent profile page

## Hour 6-7: Deploy (1 hour)

- Backend → Render or Railway (deployments/)
- Frontend → Vercel
- Update NEXT_PUBLIC_API_URL and CORS_ORIGINS

## Hour 7-8: Pitch Prep (1 hour)

- Practice `pitch/demo_script.md`
- Prepare architecture slide
- Record backup video if testnet is flaky
- Submit using `pitch/final_submission_template.md`

## Decision Matrix

| Time Left | Do This |
|-----------|---------|
| 6+ hours | Full marketplace + contract |
| 4 hours | Multi-agent demo + wallet display |
| 2 hours | Demo page workflow + mock blockchain |
| 1 hour | Polish demo script, deploy frontend |

## Don't Do

- ❌ Rewrite the entire backend
- ❌ Add auth/OAuth
- ❌ Build custom UI from scratch
- ❌ Commit private keys

## Do

- ✅ Use mock mode if API keys fail
- ✅ Show pipeline steps visually
- ✅ Have offline backup (screenshots/video)
- ✅ Lead demo with user problem
