#ifndef DOM_SESSION_H
#define DOM_SESSION_H

#include <string>
#include "dom_paths.h"
#include "dom_instance.h"
#include "dom_packset.h"

extern "C" {
#include "domino/sys.h"
#include "domino/gfx.h"
#include "content/d_content.h"
#include "world/d_world.h"
#include "sim/d_sim.h"
#include "replay/d_replay.h"
#include "domino/core/fixed.h"
}

namespace dom {

struct SessionConfig {
    std::string platform_backend;   /* maps to dsys backend */
    std::string gfx_backend;        /* maps to dgfx backend */
    std::string audio_backend;      /* future */
    bool headless;
    bool tui;
};

class DomSession {
public:
    DomSession();
    ~DomSession();

    bool init(const Paths &paths,
              const InstanceInfo &inst,
              const SessionConfig &cfg);

    void shutdown();

    const Paths&        paths()    const { return m_paths; }
    const InstanceInfo& instance() const { return m_inst; }

    d_world*        world() { return m_world; }
    d_sim_context*  sim()   { return &m_sim; }

    bool is_initialized() const { return m_initialized; }

private:
    bool init_engine(const SessionConfig &cfg);
    bool load_content(const PackSet &pset);
    bool create_world(const InstanceInfo &inst);

private:
    Paths        m_paths;
    InstanceInfo m_inst;
    PackSet      m_packset;

    d_world         *m_world;
    d_sim_context    m_sim;
    d_replay_context m_replay;

    bool m_engine_initialized;
    bool m_initialized;
};

} // namespace dom

#endif
