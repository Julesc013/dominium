import argparse
import os
import subprocess
import sys


def run_cmd(cmd, expect_code=0, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout or ""
    if expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False, output
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False, output
    return True, output


def parse_kv(output):
    data = {}
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def require_flag(data, flag_mask, message):
    try:
        flags = int(data.get("flags", "0"))
    except ValueError:
        flags = 0
    return require((flags & flag_mask) != 0, message)


def main():
    parser = argparse.ArgumentParser(description="Economy T20 integration tests.")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    tool_path = os.path.abspath(args.tool)
    repo_root = os.path.abspath(args.repo_root)
    fixture_root = os.path.join(repo_root, "tests", "fixtures", "economy")

    fixtures = [
        "local_market.economy",
        "black_market.economy",
        "remote_trade.economy",
        "shortage_spike.economy",
    ]

    ok = True
    ok = ok and require(os.path.isfile(tool_path), "economy tool missing")
    ok = ok and require(os.path.isdir(fixture_root), "economy fixtures missing")

    for fixture in fixtures:
        fixture_path = os.path.join(fixture_root, fixture)
        ok = ok and require(os.path.isfile(fixture_path), "missing fixture {}".format(fixture_path))
        if not ok:
            return 1
        success, _output = run_cmd(
            [
                tool_path,
                "validate",
                "--fixture",
                fixture_path,
            ],
            expect_contains=[
                "DOMINIUM_ECONOMY_VALIDATE_V1",
                "provider_chain=containers->storages->transports->jobs->markets->offers->bids->transactions",
            ],
        )
        ok = ok and success

    base_fixture = os.path.join(fixture_root, "local_market.economy")
    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--container",
            "logistics.container.a",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=container",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "container_id",
            "capacity_q48",
            "contents_amount_q48",
            "integrity_q16",
            "owner_ref_id",
            "location_ref_id",
            "storage_ref_id",
            "provenance_id",
            "region_id",
            "flags",
            "meta.status",
            "meta.refusal_reason",
            "budget.used",
        ):
            ok = ok and require(key in data, "container inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--storage",
            "logistics.storage.hub",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=storage",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "storage_id",
            "location_ref_id",
            "capacity_q48",
            "stored_amount_q48",
            "decay_rate_q16",
            "integrity_q16",
            "risk_profile_id",
            "provenance_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "storage inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--transport",
            "logistics.transport.cart",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=transport",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "transport_id",
            "vehicle_ref_id",
            "route_ref_id",
            "capacity_q48",
            "cargo_amount_q48",
            "travel_cost_q16",
            "risk_modifier_q16",
            "origin_ref_id",
            "destination_ref_id",
            "departure_tick",
            "arrival_tick",
            "provenance_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "transport inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--job",
            "logistics.job.delivery",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=job",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "job_id",
            "job_type",
            "task_graph_ref_id",
            "worker_ref_id",
            "required_skill_ref_id",
            "energy_cost_q48",
            "duration_ticks",
            "scheduled_tick",
            "input_ref_id",
            "output_ref_id",
            "risk_profile_id",
            "provenance_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "job inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--market",
            "market.place.town",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=market",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "market_id",
            "location_ref_id",
            "jurisdiction_ref_id",
            "listing_capacity_q48",
            "transaction_fee_q16",
            "info_delay",
            "risk_profile_id",
            "trust_profile_id",
            "law_ref_id",
            "provenance_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "market inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--offer",
            "market.offer.grain",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=offer",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "offer_id",
            "market_id",
            "seller_ref_id",
            "goods_ref_id",
            "quantity_q48",
            "price_q48",
            "exchange_medium_ref_id",
            "expiry_tick",
            "risk_profile_id",
            "trust_profile_id",
            "provenance_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "offer inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--bid",
            "market.bid.grain",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=bid",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "bid_id",
            "market_id",
            "buyer_ref_id",
            "goods_ref_id",
            "quantity_q48",
            "price_q48",
            "exchange_medium_ref_id",
            "expiry_tick",
            "risk_profile_id",
            "trust_profile_id",
            "provenance_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "bid inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--transaction",
            "market.transaction.grain",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=transaction",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "transaction_id",
            "market_id",
            "offer_id",
            "bid_id",
            "buyer_ref_id",
            "seller_ref_id",
            "goods_ref_id",
            "quantity_q48",
            "price_q48",
            "exchange_medium_ref_id",
            "transport_ref_id",
            "executed_tick",
            "risk_profile_id",
            "provenance_id",
            "region_id",
            "flags",
        ):
            ok = ok and require(key in data, "transaction inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "inspect",
            "--fixture",
            base_fixture,
            "--region",
            "economy.region.primary",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_INSPECT_V1",
            "entity=region",
        ],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        for key in (
            "region_id",
            "container_count",
            "storage_count",
            "transport_count",
            "job_count",
            "market_count",
            "offer_count",
            "bid_count",
            "transaction_count",
            "goods_total_q48",
            "price_avg_q48",
            "transaction_volume_total_q48",
            "flags",
        ):
            ok = ok and require(key in data, "region inspect missing {}".format(key))

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "economy.region.primary",
            "--tick",
            "20",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=[
            "DOMINIUM_ECONOMY_RESOLVE_V1",
            "provider_chain=containers->storages->transports->jobs->markets->offers->bids->transactions",
        ],
    )
    ok = ok and success
    resolve_hash = None
    if success:
        data = parse_kv(output)
        for key in (
            "container_count",
            "storage_count",
            "transport_count",
            "transport_arrived_count",
            "job_count",
            "job_completed_count",
            "market_count",
            "offer_count",
            "bid_count",
            "transaction_count",
            "transaction_settled_count",
            "goods_total_q48",
            "price_avg_q48",
            "transaction_volume_total_q48",
            "flags",
            "ok",
            "resolve_hash",
        ):
            ok = ok and require(key in data, "resolve missing {}".format(key))
        resolve_hash = data.get("resolve_hash")

    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            base_fixture,
            "--region",
            "economy.region.primary",
            "--tick",
            "20",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_ECONOMY_RESOLVE_V1"],
    )
    ok = ok and success
    if success and resolve_hash is not None:
        repeat_hash = parse_kv(output).get("resolve_hash")
        ok = ok and require(repeat_hash == resolve_hash, "determinism hash mismatch")

    shortage_fixture = os.path.join(fixture_root, "shortage_spike.economy")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            shortage_fixture,
            "--region",
            "economy.region.primary",
            "--tick",
            "20",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_ECONOMY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require_flag(data, 2, "shortage flag missing")

    black_fixture = os.path.join(fixture_root, "black_market.economy")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            black_fixture,
            "--region",
            "economy.region.primary",
            "--tick",
            "20",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_ECONOMY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require_flag(data, 16, "black market flag missing")

    remote_fixture = os.path.join(fixture_root, "remote_trade.economy")
    success, output = run_cmd(
        [
            tool_path,
            "resolve",
            "--fixture",
            remote_fixture,
            "--region",
            "economy.region.primary",
            "--tick",
            "20",
            "--delta",
            "1",
            "--budget",
            "200",
        ],
        expect_contains=["DOMINIUM_ECONOMY_RESOLVE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require_flag(data, 4, "congestion flag missing")

    success, output = run_cmd(
        [
            tool_path,
            "collapse",
            "--fixture",
            base_fixture,
            "--region",
            "economy.region.primary",
        ],
        expect_contains=["DOMINIUM_ECONOMY_COLLAPSE_V1"],
    )
    ok = ok and success
    if success:
        data = parse_kv(output)
        ok = ok and require(data.get("capsule_count_after") != "0", "collapse did not create capsule")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
