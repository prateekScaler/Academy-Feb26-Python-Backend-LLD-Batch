"""
LLD-38  |  Cloud-native patterns (adapted for Python)
=====================================================
DELIVERABLE 4 — A TOY SERVICE REGISTRY (standard library only)

WHY DOES THIS EXIST? (the "service discovery" problem)
------------------------------------------------------
In the old world you deployed ONE server at a fixed IP, and everyone hard-coded
that IP. In the cloud, a service like "payments" runs as MANY interchangeable
copies ("instances"), each on some ephemeral IP/port, and they come and go all
the time (autoscaling, crashes, deploys, moving between machines).

So "where is payments?" is no longer a constant. We need two things:

  1. A REGISTRY  — a live phone book: every instance REGISTERS itself
     ("payments is at 10.0.0.7:8080") and sends periodic HEARTBEATS so the
     registry knows it's still alive. Miss enough heartbeats -> you're evicted.

  2. DISCOVERY   — when service A wants to call payments, it asks the registry
     "give me a healthy payments instance", and the registry hands one back,
     spreading load across instances (here: simple ROUND-ROBIN).

This file is a ~in-memory toy so the idea is concrete without a real cluster.

HOW THE TOY MAPS TO THE REAL THING
----------------------------------
  * The dict below            ~= the key/value store inside Consul or etcd.
  * register()/deregister()   ~= a service registering with Consul's agent, or
                                 writing its key into etcd.
  * heartbeat() + TTL         ~= Consul/etcd health checks & lease TTLs; miss the
                                 lease renewal and your key is auto-removed.
  * discover() round-robin    ~= a client-side load balancer (Ribbon/gRPC LB) or
                                 Consul DNS returning healthy instances.

  * KUBERNETES does this for you WITHOUT app code: a Service gets a stable DNS
    name + virtual IP; kubelet runs readiness probes (the heartbeat equivalent);
    Endpoints/EndpointSlices track only the READY pods; and kube-proxy (iptables/
    IPVS) load-balances the virtual IP across them. So "payments" is just a DNS
    name and the platform hides all of the below.
"""

import time
import threading


class NoHealthyInstanceError(Exception):
    """Raised by discover() when a service has zero healthy instances
    (or is completely unknown)."""


class _Instance:
    """One registered copy of a service."""
    def __init__(self, address, now):
        self.address = address          # e.g. "10.0.0.1:8080"
        self.healthy = True             # explicit health flag
        self.last_heartbeat = now       # monotonic timestamp of last heartbeat


class ServiceRegistry:
    def __init__(self, heartbeat_ttl=1.0):
        # service_name -> list[_Instance]
        self._services = {}
        # service_name -> round-robin cursor (which healthy instance is next)
        self._rr = {}
        # If we don't hear a heartbeat within this many seconds, the instance is
        # considered DEAD and drops out of discovery (lease expiry).
        self._ttl = heartbeat_ttl
        self._lock = threading.Lock()

    @staticmethod
    def _now():
        return time.monotonic()

    def register(self, service_name, address):
        with self._lock:
            instances = self._services.setdefault(service_name, [])
            if any(i.address == address for i in instances):
                print(f"  registry: {service_name}@{address} already registered")
                return
            instances.append(_Instance(address, self._now()))
            self._rr.setdefault(service_name, 0)
            print(f"  registry: REGISTER {service_name} -> {address} "
                  f"(now {len(instances)} instance(s))")

    def deregister(self, service_name, address):
        with self._lock:
            instances = self._services.get(service_name, [])
            self._services[service_name] = [i for i in instances if i.address != address]
            print(f"  registry: DEREGISTER {service_name} -> {address}")

    def heartbeat(self, service_name, address):
        """An instance calls this periodically to say 'I'm still alive'."""
        with self._lock:
            for inst in self._services.get(service_name, []):
                if inst.address == address:
                    inst.last_heartbeat = self._now()
                    inst.healthy = True
                    print(f"  registry: heartbeat OK  {service_name}@{address}")
                    return
            print(f"  registry: heartbeat for unknown {service_name}@{address}")

    def mark_unhealthy(self, service_name, address):
        """Explicitly flag an instance as unhealthy (e.g. a failing health check)."""
        with self._lock:
            for inst in self._services.get(service_name, []):
                if inst.address == address:
                    inst.healthy = False
                    print(f"  registry: MARK UNHEALTHY {service_name}@{address}")
                    return

    def _is_healthy(self, inst):
        # Healthy = explicitly healthy AND heartbeat is fresh (lease not expired).
        fresh = (self._now() - inst.last_heartbeat) <= self._ttl
        return inst.healthy and fresh

    def discover(self, service_name):
        """Return the address of ONE healthy instance, round-robin.
        Raises NoHealthyInstanceError if there are none."""
        with self._lock:
            instances = self._services.get(service_name)
            if not instances:
                raise NoHealthyInstanceError(f"unknown service '{service_name}'")
            healthy = [i for i in instances if self._is_healthy(i)]
            if not healthy:
                raise NoHealthyInstanceError(
                    f"no healthy instance for '{service_name}'")
            # Round-robin: pick the cursor position, then advance it.
            idx = self._rr[service_name] % len(healthy)
            self._rr[service_name] += 1
            return healthy[idx].address


# ===========================================================================
# DEMO — run this file directly:  python3 service_registry.py
# ===========================================================================
def demo():
    print("=" * 72)
    print("SERVICE REGISTRY DEMO  (heartbeat TTL = 1.0s)")
    print("=" * 72)

    reg = ServiceRegistry(heartbeat_ttl=1.0)

    print("\n1) Register 3 instances of 'payments':")
    reg.register("payments", "10.0.0.1:8080")
    reg.register("payments", "10.0.0.2:8080")
    reg.register("payments", "10.0.0.3:8080")

    print("\n2) discover('payments') 6x -> watch ROUND-ROBIN rotate 1->2->3->1...:")
    for n in range(1, 7):
        print(f"   discover #{n} -> {reg.discover('payments')}")

    print("\n3) Mark 10.0.0.2 unhealthy (failed health check) -> it drops out:")
    reg.mark_unhealthy("payments", "10.0.0.2:8080")
    for n in range(1, 5):
        print(f"   discover #{n} -> {reg.discover('payments')}   "
              f"(only .1 and .3 now)")

    print("\n4) Let 10.0.0.1's heartbeat EXPIRE (no renewal for > TTL) while")
    print("   .3 keeps heartbeating -> .1's lease lapses and it drops out too:")
    time.sleep(1.1)                     # .1 goes stale (TTL = 1.0s)
    reg.heartbeat("payments", "10.0.0.3:8080")   # .3 renews its lease
    for n in range(1, 4):
        print(f"   discover #{n} -> {reg.discover('payments')}   "
              f"(only .3 is fresh & healthy now)")

    print("\n5) discover an UNKNOWN service -> clear 'no instance' error:")
    try:
        reg.discover("inventory")
    except NoHealthyInstanceError as e:
        print(f"   discover('inventory') raised NoHealthyInstanceError: {e}")

    print("\n6) Deregister the last healthy 'payments' instance -> now none left:")
    reg.deregister("payments", "10.0.0.3:8080")
    try:
        reg.discover("payments")
    except NoHealthyInstanceError as e:
        print(f"   discover('payments') raised NoHealthyInstanceError: {e}")

    print("\n" + "=" * 72)
    print("Done. Discovery only ever returned HEALTHY instances, load-balanced.")
    print("=" * 72)


if __name__ == "__main__":
    demo()
