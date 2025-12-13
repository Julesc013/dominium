#include "dom_packset.h"

#include <cstdio>
#include <vector>

extern "C" {
#include "domino/sys.h"
}

namespace dom {

namespace {

static bool read_file(const std::string &path, std::vector<unsigned char> &out) {
    void *fh;
    long size;
    size_t read_len;

    fh = dsys_file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }

    if (dsys_file_seek(fh, 0L, SEEK_END) != 0) {
        dsys_file_close(fh);
        return false;
    }
    size = dsys_file_tell(fh);
    if (size <= 0L) {
        dsys_file_close(fh);
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_SET) != 0) {
        dsys_file_close(fh);
        return false;
    }

    out.resize(static_cast<size_t>(size));
    read_len = dsys_file_read(fh, &out[0], static_cast<size_t>(size));
    dsys_file_close(fh);
    if (read_len != static_cast<size_t>(size)) {
        out.clear();
        return false;
    }
    return true;
}

static bool load_blob_from(const std::string &path,
                           std::vector<unsigned char> &storage,
                           d_tlv_blob &blob) {
    std::vector<unsigned char> data;
    if (!read_file(path, data)) {
        return false;
    }
    storage.swap(data);
    blob.ptr = storage.empty() ? (unsigned char *)0 : &storage[0];
    blob.len = static_cast<unsigned int>(storage.size());
    return true;
}

static std::string version_string(unsigned v) {
    char buf[32];
    std::sprintf(buf, "%08u", v);
    return std::string(buf);
}

} // namespace

bool PackSet::load_for_instance(const Paths &paths, const InstanceInfo &inst) {
    size_t i;

    pack_blobs.clear();
    mod_blobs.clear();
    m_pack_storage.clear();
    m_mod_storage.clear();
    base_loaded = false;
    base_version = 0u;

    /* Auto-load base pack first if present. */
    {
        const unsigned kBasePackVersion = 1u;
        d_tlv_blob blob;
        std::vector<unsigned char> storage;
        std::string version = version_string(kBasePackVersion);
        std::string pack_dir = join(paths.packs, "base");
        std::string ver_dir = join(pack_dir, version);
        std::string tlv_path = join(ver_dir, "pack.tlv");
        std::string bin_path = join(ver_dir, "pack.bin");

        if (load_blob_from(tlv_path, storage, blob) || load_blob_from(bin_path, storage, blob)) {
            m_pack_storage.push_back(std::vector<unsigned char>());
            m_pack_storage.back().swap(storage);
            blob.ptr = m_pack_storage.back().empty() ? (unsigned char *)0 : &m_pack_storage.back()[0];
            blob.len = static_cast<unsigned int>(m_pack_storage.back().size());
            pack_blobs.push_back(blob);
            base_loaded = true;
            base_version = kBasePackVersion;
        }
    }

    for (i = 0u; i < inst.packs.size(); ++i) {
        const PackRef &pref = inst.packs[i];
        d_tlv_blob blob;
        std::vector<unsigned char> storage;
        std::string version = version_string(pref.version);
        std::string pack_dir = join(paths.packs, pref.id);
        std::string ver_dir = join(pack_dir, version);
        std::string tlv_path = join(ver_dir, "pack.tlv");
        std::string bin_path = join(ver_dir, "pack.bin");

        if (!load_blob_from(tlv_path, storage, blob)) {
            if (!load_blob_from(bin_path, storage, blob)) {
                return false;
            }
        }

        m_pack_storage.push_back(std::vector<unsigned char>());
        m_pack_storage.back().swap(storage);
        blob.ptr = m_pack_storage.back().empty() ? (unsigned char *)0 : &m_pack_storage.back()[0];
        blob.len = static_cast<unsigned int>(m_pack_storage.back().size());
        pack_blobs.push_back(blob);
    }

    for (i = 0u; i < inst.mods.size(); ++i) {
        const ModRef &mref = inst.mods[i];
        d_tlv_blob blob;
        std::vector<unsigned char> storage;
        std::string version = version_string(mref.version);
        std::string mod_dir = join(paths.mods, mref.id);
        std::string ver_dir = join(mod_dir, version);
        std::string tlv_path = join(ver_dir, "mod.tlv");
        std::string bin_path = join(ver_dir, "mod.bin");

        if (!load_blob_from(tlv_path, storage, blob)) {
            if (!load_blob_from(bin_path, storage, blob)) {
                return false;
            }
        }

        m_mod_storage.push_back(std::vector<unsigned char>());
        m_mod_storage.back().swap(storage);
        blob.ptr = m_mod_storage.back().empty() ? (unsigned char *)0 : &m_mod_storage.back()[0];
        blob.len = static_cast<unsigned int>(m_mod_storage.back().size());
        mod_blobs.push_back(blob);
    }

    /* TODO: dependency resolution and conflict detection. */
    return true;
}

} // namespace dom
