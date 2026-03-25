# Class 10: Quick Revision Guide - AWS, EC2 & RDS

Use this to revise before interviews or when you need a refresher.

---

## 1. Cloud Computing Basics

### What is "The Cloud"?
Someone else's computers that you rent over the internet instead of buying your own.

### Why Cloud vs Buying Servers?
| Factor | Buy (On-Premise) | Rent (Cloud) |
|--------|------------------|--------------|
| Upfront cost | $50,000+ | $0 (pay as you go) |
| Time to start | Weeks/months | Minutes |
| Scaling | Buy more hardware | Click a button |
| Maintenance | You fix everything | Provider handles it |
| If startup fails | Stuck with servers | Stop paying, walk away |

### When Cloud Might NOT Be the Best Choice
- **Predictable, high workloads** - If you're running at 80%+ capacity 24/7, owning hardware can be cheaper
- **Data sovereignty** - Some industries require data on your own premises
- **Specialized hardware** - Custom GPUs, FPGAs that cloud doesn't offer
- **Long-term costs** - After ~3 years, owned hardware often becomes cheaper

> Companies like Basecamp and Dukaan have moved away from cloud to save costs. But this makes sense only at scale with dedicated DevOps teams.

### Service Models
```
IaaS (Infrastructure) → You manage OS, runtime, app
PaaS (Platform)       → You manage app only
SaaS (Software)       → You just use it
```

**Pizza Analogy:**
- IaaS = Buy ingredients, make pizza yourself (EC2)
- PaaS = Buy pre-made dough, add toppings (Heroku, Render)
- SaaS = Order Domino's delivery (Gmail, Slack)

### Regions & Availability Zones
- **Region** = Geographic location (e.g., ap-south-1 = Mumbai)
- **AZ** = Independent data center within a region

Choose region based on:
1. **Latency** - Close to your users (Hotstar uses Mumbai for Indian users)
2. **Cost** - US regions are often cheapest
3. **Compliance** - Data residency laws (India's data localization)

---

## 2. Networking Fundamentals

### IP Addresses & CIDR Notation

**IPv4 Address** - A 32-bit number written as 4 octets:
```
192.168.1.5 = 11000000.10101000.00000001.00000101
              (8 bits)  (8 bits)  (8 bits)  (8 bits) = 32 bits
```

**CIDR Notation** - The `/number` tells how many bits are the network part:

| CIDR | Meaning | Available IPs | Example |
|------|---------|---------------|---------|
| `/32` | All 32 bits fixed | 1 (exact IP) | `192.168.1.5/32` = only that IP |
| `/24` | First 24 bits fixed | 256 | `192.168.1.0/24` = 192.168.1.0 to .255 |
| `/16` | First 16 bits fixed | 65,536 | `192.168.0.0/16` = 192.168.x.x |
| `/0` | No bits fixed | ~4.3 billion | `0.0.0.0/0` = anywhere! |

**Why IPv6?**
- IPv4 = 32 bits = ~4.3 billion addresses (not enough!)
- IPv6 = 128 bits = 340 undecillion addresses
- IPv6 looks like: `2001:0db8:85a3:0000:0000:8a2e:0370:7334`

**In AWS Security Groups:**
- `0.0.0.0/0` = Allow from any IPv4
- `::/0` = Allow from any IPv6

### Common Ports
| Port | Protocol | Used For |
|------|----------|----------|
| 22 | SSH | Remote terminal access |
| 80 | HTTP | Web traffic (unencrypted) |
| 443 | HTTPS | Web traffic (encrypted) |
| 5432 | PostgreSQL | Database connections |
| 3306 | MySQL | Database connections |
| 6379 | Redis | Cache/message broker |

### Forward Proxy vs Reverse Proxy

This is a **very common interview question**!

```
FORWARD PROXY (client-side):
┌────────┐     ┌─────────────┐     ┌──────────┐
│ Client │ ──► │ Forward     │ ──► │ Internet │
│        │     │ Proxy       │     │ (Server) │
└────────┘     └─────────────┘     └──────────┘
Client knows about proxy, server doesn't.

REVERSE PROXY (server-side):
┌────────┐     ┌─────────────┐     ┌──────────┐
│ Client │ ──► │ Reverse     │ ──► │ Your     │
│        │     │ Proxy       │     │ Server   │
└────────┘     └─────────────┘     └──────────┘
Server knows about proxy, client doesn't.
```

**Forward Proxy (Client's Helper)**
- Sits in front of **clients**
- Client explicitly configures to use the proxy
- Use cases:
  - **Corporate firewalls** - Block employees from accessing certain sites
  - **Anonymity** - Hide client's IP from servers (like VPNs)
  - **Caching** - Cache frequently accessed content for faster access
  - **Access control** - Schools blocking social media

**Reverse Proxy (Server's Helper)**
- Sits in front of **servers**
- Client doesn't know it exists
- Use cases:
  - **Load balancing** - Distribute requests across multiple servers
  - **SSL termination** - Handle HTTPS, forward HTTP internally
  - **Caching** - Cache responses to reduce server load
  - **Security** - Hide server IPs, add WAF protection
  - **Compression** - Gzip responses before sending

**Real-World Examples:**
| Type | Examples |
|------|----------|
| Forward Proxy | Squid, corporate firewalls, VPNs |
| Reverse Proxy | Nginx, HAProxy, AWS ALB, Cloudflare |

**The Key Difference:**
- Forward proxy: **Protects clients** (hides who's making requests)
- Reverse proxy: **Protects servers** (hides what's serving responses)

---

## 3. EC2 (Elastic Compute Cloud)

### What is EC2?
Virtual servers you can launch in minutes.

### Instance Types
Format: `t2.medium`
- **First letter** = Family (t=general, c=compute, r=memory)
- **Number** = Generation (higher = newer)
- **Size** = nano → micro → small → medium → large → xlarge

| Family | Optimized For | Use Case |
|--------|---------------|----------|
| T (t2, t3) | General purpose, burstable | Web servers, small apps |
| M (m5, m6i) | Balanced CPU/memory | Production apps |
| C (c5, c6i) | CPU intensive | Video encoding, ML inference |
| R (r5, r6i) | Memory intensive | Databases, caching |

**For learning:** Use `t2.micro` or `t3.micro` (Free Tier!)

### Key Concepts

**AMI (Amazon Machine Image)**
- Template with OS + pre-installed software
- Examples: Ubuntu 22.04, Amazon Linux 2023

**Key Pair**
- SSH key to connect to your instance
- Download `.pem` file - **you can't get it again!**

**Security Group**
- Virtual firewall controlling inbound/outbound traffic
- Stateful: if you allow inbound, response is auto-allowed

**EBS (Elastic Block Store)**
- Persistent hard drive for your instance
- Data survives instance stop/restart

### Security Group Rules
```
INBOUND (traffic coming IN):
┌──────────┬──────────┬─────────────────┐
│ Type     │ Port     │ Source          │
├──────────┼──────────┼─────────────────┤
│ SSH      │ 22       │ My IP only!     │
│ HTTP     │ 80       │ 0.0.0.0/0       │
│ HTTPS    │ 443      │ 0.0.0.0/0       │
└──────────┴──────────┴─────────────────┘

⚠️ NEVER open SSH (port 22) to 0.0.0.0/0
   Bots constantly scan for open SSH ports!
```

### File Permissions (chmod)

```
Permission types:     r (read) = 4
                      w (write) = 2
                      x (execute) = 1

Three categories:     Owner | Group | Others

chmod 400 my-key.pem
       │││
       ││└── Others: 0 (no access)
       │└─── Group: 0 (no access)
       └──── Owner: 4 (read only)

Common values:
  400 = Owner read only (for private keys)
  644 = Owner read/write, others read (for public files)
  755 = Owner all, others read/execute (for scripts)
```

### Launching & Connecting
```bash
# 1. Set key permissions (required!)
chmod 400 my-key.pem

# 2. SSH into instance
ssh -i my-key.pem ubuntu@<your-ec2-public-ip>

# Breaking down the command:
# ssh     = Secure Shell command
# -i      = Identity file (private key)
# ubuntu  = Username (depends on AMI)
# @IP     = The server's public IP
```

### Setting Up Django on EC2
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Create project directory
mkdir ~/myproject && cd ~/myproject
python3 -m venv venv
source venv/bin/activate

# Install Django + Gunicorn
pip install django gunicorn

# Run development server (accessible from outside)
python manage.py runserver 0.0.0.0:8000
```

---

## 4. Production Deployment

### Why Not Just `runserver`?

Django's `runserver` is for development only:
- Single-threaded (one request at a time)
- No security hardening
- Restarts on code changes (bad in production!)

### Production Stack

```
Internet → Nginx (reverse proxy) → Gunicorn → Django
              │
              ├── Handles HTTPS/SSL
              ├── Serves static files
              ├── Load balances
              └── Caches responses
```

**Gunicorn** = Python WSGI HTTP Server
- Runs multiple worker processes
- Each worker handles requests concurrently
- `gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers 3`

**Nginx** = Reverse Proxy
- Sits in front of Gunicorn
- Handles SSL termination (HTTPS → HTTP internally)
- Serves static files directly (CSS, JS, images)
- Buffers slow clients (protects Gunicorn)

### Quick Gunicorn Setup
```bash
# Install
pip install gunicorn

# Run (3 workers, binding to all interfaces)
gunicorn mysite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3

# Workers formula: (2 × CPU cores) + 1
```

---

## 5. RDS (Relational Database Service)

### What is RDS?
Managed database service. AWS handles backups, patches, failover.

### Why RDS vs Installing on EC2?
| Task | Self-Managed (EC2) | RDS |
|------|-------------------|-----|
| Install database | You | AWS |
| Security patches | You | AWS |
| Backups | You set up cron | Automatic daily |
| 3 AM crash | You wake up | AWS handles it |
| Multi-AZ failover | Complex setup | One checkbox |

### Supported Databases
PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Aurora

**For Django:** PostgreSQL is most common and recommended.

### RDS Security Group
```
⚠️ CRITICAL: RDS should NEVER be publicly accessible!

INBOUND:
┌──────────────┬──────────┬─────────────────────────┐
│ Type         │ Port     │ Source                  │
├──────────────┼──────────┼─────────────────────────┤
│ PostgreSQL   │ 5432     │ EC2 Security Group ID   │
└──────────────┴──────────┴─────────────────────────┘

Only your EC2 instances should talk to the database!
```

### Connect Django to RDS
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'admin',
        'PASSWORD': 'your-password',  # Use environment variables!
        'HOST': 'mydb.xxxxx.ap-south-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}
```

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Test connection
python manage.py migrate
```

### Connection Troubleshooting
1. **Security Group** - RDS must allow EC2's security group
2. **Endpoint** - Copy exact endpoint from RDS console
3. **Credentials** - Must match what you set during creation
4. **psycopg2** - Must be installed

```bash
# Test raw connectivity
telnet your-rds-endpoint 5432
# "Connected" = security group correct
# Hangs = security group blocking
```

---

## 6. AWS Services Quick Reference

| Service | Purpose |
|---------|---------|
| **EC2** | Virtual servers (compute) |
| **RDS** | Managed databases |
| **S3** | Object storage (files, images, backups) |
| **Route 53** | DNS (domain names) |
| **CloudFront** | CDN (cache content at edge locations) |
| **ElastiCache** | Managed Redis/Memcached |
| **ALB** | Application Load Balancer |
| **VPC** | Virtual Private Cloud (networking) |
| **IAM** | Identity & Access Management |
| **CloudWatch** | Monitoring & logs |

---

## 7. Free Tier Limits (12 months)

| Service | Free Limit |
|---------|------------|
| EC2 | 750 hours/month t2.micro |
| RDS | 750 hours/month db.t2.micro |
| S3 | 5 GB storage |
| Data Transfer | 15 GB/month outbound |

**Avoid surprise bills:**
- Set up billing alerts ($5, $10, $20 thresholds)
- Stop EC2 instances when not using
- Delete unused RDS (costs even when stopped after 7 days!)
- Check billing dashboard weekly

---

## 8. Deployment Checklist

- [ ] Launch EC2 (Ubuntu, t2.micro, Free Tier)
- [ ] Configure EC2 Security Group (SSH from My IP, HTTP/HTTPS from anywhere)
- [ ] Create RDS (PostgreSQL, db.t3.micro)
- [ ] Configure RDS Security Group (allow EC2's security group only)
- [ ] SSH into EC2
- [ ] Install Python, Django, Gunicorn, psycopg2
- [ ] Configure Django settings (DATABASES, ALLOWED_HOSTS)
- [ ] Run migrations
- [ ] Run with Gunicorn (not runserver!)
- [ ] (Optional) Set up Nginx as reverse proxy

---

## 9. Quick Self-Test

1. What does IaaS stand for?
2. What is an Availability Zone?
3. What instance type is in the Free Tier?
4. What port does PostgreSQL use?
5. Why should RDS not be publicly accessible?
6. What does `/24` mean in CIDR notation?
7. What's the difference between a forward proxy and reverse proxy?
8. Why use Nginx in front of Gunicorn?

<details>
<summary>Answers</summary>

1. Infrastructure as a Service
2. Independent data center within a region (for high availability)
3. t2.micro or t3.micro
4. 5432
5. Security - database should only be reachable from application servers, not the internet
6. First 24 bits are network address, last 8 bits are host addresses (256 IPs)
7. Forward proxy sits in front of clients (hides clients), reverse proxy sits in front of servers (hides servers)
8. SSL termination, serve static files, buffer slow clients, load balancing

</details>

---

## 10. Common Interview Questions

**Q: What's the difference between EC2 and RDS?**
EC2 is virtual servers (compute), RDS is managed databases. You could run a database on EC2, but RDS handles backups, patches, and failover automatically.

**Q: What's a Security Group?**
A virtual firewall that controls inbound and outbound traffic to AWS resources. It's stateful - if inbound is allowed, the response is automatically allowed out.

**Q: How do you make an application highly available?**
Deploy across multiple Availability Zones. Use a load balancer (ALB) to distribute traffic. Use RDS Multi-AZ for database failover.

**Q: What's the difference between a Region and an AZ?**
Region is a geographic location (Mumbai, Oregon). AZ is an independent data center within that region. Multiple AZs provide redundancy if one data center fails.

**Q: Explain forward proxy vs reverse proxy.**
- Forward proxy: Sits in front of clients. Client knows about it, server doesn't. Used for: corporate firewalls, VPNs, anonymity.
- Reverse proxy: Sits in front of servers. Server knows about it, client doesn't. Used for: load balancing, SSL termination, caching, security.

**Q: Why use Nginx with Django in production?**
Django's `runserver` is single-threaded and not secure. Gunicorn handles multiple Python workers. Nginx in front handles SSL, serves static files efficiently, buffers slow clients, and can load balance across multiple Gunicorn instances.

**Q: What is CIDR notation?**
A way to specify IP ranges. The number after `/` indicates how many bits are the network portion. `/24` means 256 IPs, `/16` means 65,536 IPs, `/0` means all IPs.

**Q: How would you secure an RDS database?**
- Put it in a private subnet (no public IP)
- Security group allows only your EC2 instances
- Use SSL for connections
- Enable encryption at rest
- Regular backups with point-in-time recovery
