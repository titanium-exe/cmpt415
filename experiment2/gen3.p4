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

struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
}

struct metadata {
    // Define your metadata fields here
}

parser MyParser(packet_in packet, out headers hdr) {
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

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    Register<bit<32>>(1) ipv4_packet_count;
    action count_ipv4_packets() {
        bit<32> count;
        ipv4_packet_count.read(count, 0);
        count = count + 1;
        ipv4_packet_count.write(0, count);
    }
    table count_ipv4_table {
        key = {
            hdr.ipv4.version: exact;
        }
        actions = {
            count_ipv4_packets;
        }
        default_action = count_ipv4_packets();
    }
    apply {
        count_ipv4_table.apply();
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

V1Switch(
    MyParser(),
    MyIngress(),
    MyEgress(),
    MyDeparser()
) main;