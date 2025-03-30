#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4> version;
    bit<4> ihl;
    bit<8> diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3> flags;
    bit<13> fragOffset;
    bit<8> ttl;
    bit<8> protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

struct Headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
}

struct Meta {
}

parser MyParser(packet_in packet, out Headers hdr, inout Meta meta, inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x0800: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

control MyIngress(inout Headers hdr, inout Meta meta, inout standard_metadata_t standard_metadata) {
    Register<bit<32>>(1) packet_count;

    action count_packets() {
        packet_count.write(0, packet_count.read(0) + 1);
    }

    table count_ipv4_packets {
        key = {
            hdr.ipv4.version: exact;
        }
        actions = {
            count_packets;
        }
        default_action = count_packets();
    }

    apply {
        if (hdr.ipv4.isValid()) {
            count_ipv4_packets.apply();
        }
    }
}

control MyEgress(inout Headers hdr, inout Meta meta, inout standard_metadata_t standard_metadata) {
    apply { }
}

control MyDeparser(packet_out packet, in Headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

V1Switch(
    MyParser(),
    MyIngress(),
    MyEgress(),
    MyDeparser()
) main;