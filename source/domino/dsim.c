#include "domino/dsim.h"
#include "domino/dzone.h"
#include "domino/dnet.h"
#include "domino/dactor.h"
#include "domino/dvehicle.h"
#include "domino/dmachine.h"
#include "domino/dresearch.h"
#include "domino/djob.h"

void dsim_tick(SimTick t)
{
    dzone_tick(t);
    dnet_power_step(1);
    dnet_fluid_step(1);
    dnet_gas_step(1);
    dnet_heat_step(1);
    dnet_signal_step(1);
    dnet_data_step(1);
    dnet_comm_step(1);
    dactor_tick_all(t);
    dvehicle_tick_all(t, 1);
    dmachine_tick_all(t);
    dresearch_tick(t);
    djob_tick(t);
}
