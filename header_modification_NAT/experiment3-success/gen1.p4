#include <core.p4>
#include <v1model.p4>

#define IP_ADDR 0x08080808 // 8.8.8.8 in hex
#define MAC_ADDR 0x112233445566 // fixed MAC address

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

struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
}

struct metadata {
}

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action set_src_mac() {
        hdr.ethernet.srcAddr = MAC_ADDR;
    }
    action drop() {
        mark_to_drop(standard_metadata);
    }
    table my_table {
        key = {
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            set_src_mac;
            drop;
        }
        default_action = set_src_mac();
    }
    apply {
        my_table.apply();
    }
}

control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {
    }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

control NoOpChecksum(inout headers hdr, inout metadata meta) {
    apply {
    }
}

V1Switch(
    MyParser(),
    NoOpChecksum(),
    MyIngress(),
    MyEgress(),
    NoOpChecksum(),
    MyDeparser()
) main;