# Class 11: Quick Revision Guide
## Elastic Beanstalk, VPC, Route 53 & CloudWatch

---

## 1. Elastic Beanstalk (EB)

### The Problem: Manual Setup is Hard
```
To deploy Django with auto-scaling, you'd need to set up:
EC2 + ALB + Auto Scaling Group + Target Groups + CloudWatch Alarms + ...
= Days of work!
```

### The Solution: Elastic Beanstalk
```
You: Upload code
EB:  Handles EVERYTHING (EC2, load balancer, auto-scaling, monitoring)
```

**Think of it as:** Heroku built into AWS

### Key Files for EB Deployment
```
myproject/
├── requirements.txt          # Python dependencies
├── .ebextensions/
│   └── django.config         # EB configuration
└── your Django code
```

### EB CLI Commands
| Command | What It Does |
|---------|--------------|
| `eb init` | Initialize EB project (choose region, app name) |
| `eb create` | Create environment (launches EC2, ALB, etc.) |
| `eb deploy` | Deploy new code version |
| `eb open` | Open app in browser |
| `eb logs` | View application logs |
| `eb terminate` | Delete everything (stop billing!) |

### Auto-Scaling: You Control the Rules
```
Default: Scale up when CPU > 70%
You can customize:
  - Trigger metric (CPU, Memory, Network)
  - Thresholds (50%, 80%, etc.)
  - Min/Max instances
```

> **Note:** EBS (Elastic Block Store) ≠ Elastic Beanstalk. EBS = storage, EB = deployment platform.

---

## 2. VPC (Virtual Private Cloud)

### What is VPC?
Your **isolated private network** in AWS. All your resources live inside it.

### Production Architecture Diagram
```
                    🌐 INTERNET
                         │
                         ▼
            ┌────────────────────────┐
            │   INTERNET GATEWAY     │  ← Main door to internet
            └────────────────────────┘
                         │
╔════════════════════════════════════════════════════════╗
║  VPC (10.0.0.0/16)                                     ║
║                                                        ║
║    ┌──────────────────────────────────────────────┐   ║
║    │         🚦 ROUTER (Route Table)               │   ║
║    │         Decides where traffic goes            │   ║
║    └──────────────────────────────────────────────┘   ║
║              │                        │               ║
║              ▼                        ▼               ║
║  ┌─────────────────────┐  ┌─────────────────────┐    ║
║  │ 🏝️ PUBLIC SUBNET    │  │ 🔒 PRIVATE SUBNET   │    ║
║  │ 10.0.1.0/24         │  │ 10.0.2.0/24         │    ║
║  │                     │  │                     │    ║
║  │ ⚖️ Load Balancer    │  │ 💻 EC2 (Django)     │    ║
║  │ 🔧 NAT Gateway      │  │ 🗄️ RDS (Database)   │    ║
║  │ 👤 Bastion Host     │  │                     │    ║
║  │                     │  │                     │    ║
║  │ 🛡️ Security Groups  │  │ 🛡️ Security Groups  │    ║
║  └─────────────────────┘  └─────────────────────┘    ║
╚════════════════════════════════════════════════════════╝
```

### Key Components Explained

| Component | What It Is | Simple Analogy |
|-----------|------------|----------------|
| **VPC** | Your isolated network | Your apartment |
| **Subnet** | Smaller network inside VPC | Rooms in apartment |
| **Public Subnet** | Has internet access | Living room (guests allowed) |
| **Private Subnet** | No direct internet | Bedroom (private) |
| **Internet Gateway** | Connects VPC to internet | Front door |
| **NAT Gateway** | One-way internet for private subnet | Service entrance (out only) |
| **Route Table** | Traffic rules | Building directory |
| **Security Group** | Firewall per instance | Room lock |
| **Bastion Host** | SSH jump server | Reception desk |

### Public vs Private Subnet
| | Public Subnet | Private Subnet |
|---|---------------|----------------|
| **Internet Access** | Direct (via IGW) | Outbound only (via NAT) |
| **Public IP** | Yes | No |
| **Put Here** | ALB, Bastion, NAT | App servers, Databases |

### CIDR Notation (IP Ranges)
```
/16 = 65,536 IPs  → VPC         (10.0.0.0/16)
/24 = 256 IPs     → Subnet      (10.0.1.0/24)
/32 = 1 IP        → Single host (10.0.1.5/32)
```

**How?** 32 - 16 = 16 bits for hosts → 2^16 = 65,536

### Default VPC
- AWS creates one automatically in each region
- CIDR: `172.31.0.0/16`
- All subnets are PUBLIC by default
- Fine for learning, create custom VPC for production

### NAT Gateway: Why?
```
Private EC2 needs to run: pip install django

But it has no public IP! How?

Private EC2 → NAT Gateway → Internet Gateway → Internet
                  ↑
        (Lives in public subnet)
        (Translates private IP to public)
```

Cost: ~$32/month. For dev, use NAT Instance (t3.micro) instead.

---

## 3. Security Groups

### Key Fact: STATEFUL
```
Request:  Client → (Allowed) → EC2
Response: EC2 → (Auto-allowed) → Client   ← No rule needed!
```

### Security Group vs Network ACL
| | Security Group | Network ACL |
|---|----------------|-------------|
| Level | Instance | Subnet |
| Stateful | ✅ Yes | ❌ No |
| Rules | Allow only | Allow + Deny |

### SG Reference Pattern (Important!)
Instead of hardcoding IPs, reference other Security Groups:

```
Web SG:  Allow 80, 443 from 0.0.0.0/0
App SG:  Allow 8000 from Web-SG-ID      ← Not an IP!
DB SG:   Allow 5432 from App-SG-ID      ← Not an IP!
```

**Why?** EC2 IPs change. SG IDs don't. Auto-scaling friendly!

### Common Ports
| Port | Service | Allow From |
|------|---------|------------|
| 22 | SSH | Your IP only! |
| 80 | HTTP | 0.0.0.0/0 |
| 443 | HTTPS | 0.0.0.0/0 |
| 5432 | PostgreSQL | App SG |
| 3306 | MySQL | App SG |

---

## 4. Route 53 (DNS)

### Why "Route 53"?
- **Route** = DNS routes traffic to the right IP
- **53** = DNS uses port 53

### What DNS Does
```
You type:  google.com
DNS returns: 142.250.193.46
Browser connects to that IP
```

### DNS Record Types
| Type | What It Does | Example |
|------|--------------|---------|
| **A** | Domain → IP | `myapp.com → 13.232.x.x` |
| **CNAME** | Domain → Domain | `www.myapp.com → myapp.com` |
| **Alias** | Domain → AWS resource | `myapp.com → my-alb.amazonaws.com` |
| **TXT** | Text (verification) | Google site verification |
| **MX** | Mail servers | Email routing |

### A vs CNAME vs Alias
| | A Record | CNAME | Alias |
|---|----------|-------|-------|
| Works for `myapp.com` (naked domain) | ✅ | ❌ | ✅ |
| Points to | IP address | Domain | AWS resource |
| Cost | $0.40/million | $0.40/million | FREE |

**Rule:** Use Alias for ALB, CloudFront, S3

### TXT Records: Domain Verification
```
Google says: "Add this TXT record to prove you own the domain"
   google-site-verification=abc123xyz

You add it to Route 53

Google checks DNS → Finds your code → Verified! ✅
```

Used for: Google Search Console, SSL certificates, email (SPF/DKIM)

### DNS Lookup Commands
```bash
# Basic lookup
dig google.com

# See the full DNS journey
dig +trace google.com

# Check TXT records
dig TXT google.com +short
```

---

## 5. CloudWatch (Monitoring)

### What It Does
Monitors your AWS resources. First place to check when something breaks.

### Key EC2 Metrics
| Metric | What It Measures | Alert When |
|--------|------------------|------------|
| CPUUtilization | CPU usage % | > 80% sustained |
| NetworkIn/Out | Bytes transferred | Sudden spike |
| StatusCheckFailed | Instance health | Any failure |

### Memory/Disk NOT Included!
EC2 doesn't send memory metrics by default. Install CloudWatch Agent:
```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Setting Up Alarms
1. Create SNS Topic (email notifications)
2. Create CloudWatch Alarm
3. Pick metric (e.g., CPUUtilization > 80%)
4. Set action → notify SNS topic

---

## 6. Quick Reference: Traffic Flow

**User visits your Django app:**
```
1. User types myapp.com
2. DNS (Route 53) returns your IP
3. Request hits Internet Gateway
4. Router sends to Load Balancer (public subnet)
5. Security Group checks port 80/443 ✅
6. Load Balancer forwards to EC2 (private subnet)
7. Django processes request
8. Django queries RDS (private subnet)
9. Response goes back the same path
```

---

## 7. Quick Self-Test

1. What does Elastic Beanstalk handle for you?
2. What's the difference between public and private subnets?
3. Why use NAT Gateway?
4. What does "stateful" mean for Security Groups?
5. Why is the SG reference pattern better than using IPs?
6. What's the difference between A record and Alias?
7. Why doesn't CloudWatch show memory by default?

<details>
<summary>Answers</summary>

1. EC2, ALB, Auto Scaling, deployments, monitoring - everything!
2. Public has internet via IGW; Private has no public IP, uses NAT for outbound
3. Lets private subnet access internet (pip install) without exposing it
4. If inbound is allowed, response is automatically allowed
5. EC2 IPs change; SG IDs don't. Works with auto-scaling
6. A maps to IP; Alias maps to AWS resources, works at zone apex, free queries
7. CloudWatch Agent must be installed inside the EC2 to collect OS-level metrics

</details>

---

## 8. Interview Questions

**Q: Elastic Beanstalk vs EC2?**
- EC2: Just a virtual server, you configure everything
- EB: PaaS that manages EC2, ALB, auto-scaling for you

**Q: When would you NOT use Elastic Beanstalk?**
- Need fine-grained control over infrastructure
- Complex networking requirements
- Using containers (use ECS/EKS instead)

**Q: Public vs Private subnet?**
- Public: Has route to Internet Gateway, gets public IP
- Private: No public IP, uses NAT Gateway for outbound internet

**Q: Why put database in private subnet?**
- No public IP = can't be reached from internet
- Only your app servers can connect
- Defense in depth

**Q: Security Group vs NACL?**
- SG: Instance-level, stateful, allow-only
- NACL: Subnet-level, stateless, allow+deny

**Q: What's an Alias record?**
- AWS-specific DNS record
- Points to AWS resources (ALB, CloudFront)
- Unlike CNAME: works for naked domain, free queries

---

## 9. Cost Awareness

| Service | Cost |
|---------|------|
| Elastic Beanstalk | Free (pay for resources it creates) |
| NAT Gateway | ~$32/month + data transfer |
| Route 53 Hosted Zone | $0.50/month |
| Route 53 Queries | $0.40/million (Alias = free) |
| CloudWatch Alarms | $0.10/alarm/month |

**Tips:**
- Use NAT Instance (t3.micro) for dev to save $30/month
- Terminate EB environments when not using
- Set billing alerts!
