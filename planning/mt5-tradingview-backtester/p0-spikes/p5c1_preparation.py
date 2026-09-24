from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GateDenied(RuntimeError):
    pass


class AuthorizationState(str, Enum):
    PENDING = "pending_authorization"
    READY = "ready"


@dataclass(frozen=True)
class BrokerIdentity:
    account_id: str
    server: str
    mode: str
    authorized: bool = False


@dataclass(frozen=True)
class RiskPolicy:
    symbol: str
    action: str
    max_volume: float
    max_risk_pct: float


@dataclass(frozen=True)
class ExecutionIntent:
    request_id: str
    operation: str
    symbol: str
    volume: float


class BrokerIdentityGate:
    def validate(self, identity: BrokerIdentity) -> None:
        if not identity.account_id or not identity.server:
            raise GateDenied("broker identity is incomplete")
        if not identity.authorized:
            raise GateDenied("broker identity is not authorized")


class RiskPolicyGate:
    def validate(self, policy: RiskPolicy, intent: ExecutionIntent) -> None:
        if not policy.symbol or policy.symbol != intent.symbol:
            raise GateDenied("symbol scope mismatch")
        if intent.volume <= 0 or intent.volume > policy.max_volume:
            raise GateDenied("volume exceeds policy")
        if policy.max_risk_pct < 0:
            raise GateDenied("invalid risk limit")


class ExecutionGate:
    """Preparation boundary. It never sends broker execution requests."""

    def validate(self, identity: BrokerIdentity, policy: RiskPolicy, intent: ExecutionIntent) -> None:
        BrokerIdentityGate().validate(identity)
        RiskPolicyGate().validate(policy, intent)
