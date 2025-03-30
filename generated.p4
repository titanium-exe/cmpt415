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

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4> dataOffset;
    bit<4> reserved;
    bit<8> flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
    tcp_t tcp;
}

parser MyParser(packet_in packet, out headers hdr, inout standard_metadata_t standard_metadata, inout bool checksum_ok) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x0800: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w6: parse_tcp;
            default: accept;
        }
    }
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}

control MyVerifyChecksum(headers hdr, inout bool checksum_ok) {
    apply {
        if (hdr.ipv4.isValid()) {
            InternetChecksum() ck;
            ck.clear();
            ck.add({ hdr.ipv4.version,
                hdr.ipv4.ihl, hdr.ipv4.diffserv, hdr.ipv4.totalLen,
                hdr.ipv4.identification, hdr.ipv4.flags, hdr.ipv4.fragOffset,
                hdr.ipv4.ttl, hdr.ipv4.protocol, hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr });
            checksum_ok = (ck.get() == hdr.ipv4.hdrChecksum);
        }
    }
}

action drop() {
    mark_to_drop();
}

table drop_tcp_port_80 {
    key = {
        hdr.tcp.dstPort: exact;
    }
    actions = {
        drop;
    }
    default_action = NoAction();
}

control MyIngress(headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {
        if (hdr.tcp.dstPort == 80) {
            drop_tcp_port_80.apply();
        }
    }
}

control MyEgress(headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply { }
}

control MyComputeChecksum(headers hdr, inout metadata meta) {
    apply {
        if (hdr.ipv4.isValid()) {
            InternetChecksum() ck;
            ck.clear();
            ck.add({ hdr.ipv4.version,
                hdr.ipv4.ihl, hdr.ipv4.diffserv, hdr.ipv4.totalLen,
                hdr.ipv4.identification, hdr.ipv4.flags, hdr.ipv4.fragOffset,
                hdr.ipv4.ttl, hdr.ipv4.protocol, hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr });
            hdr.ipv4.hdrChecksum = ck.get();
        }
    }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
    }
}

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;