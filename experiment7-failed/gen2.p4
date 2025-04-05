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
}

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
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

control MyVerifyChecksum(headers hdr, bool computeChecksum) {
    apply {
        // Add your code here
    }
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    Register<bit<32>>(256) port_counter;

    action count_packets() {
        port_counter.write(standard_metadata.ingress_port, port_counter.read(standard_metadata.ingress_port) + 1);
    }

    table count_ipv4_packets {
        key = {
            hdr.ipv4.isValid(): exact;
        }
        actions = {
            count_packets;
        }
        default_action = count_packets;
    }

    apply {
        count_ipv4_packets.apply();
        if (!hdr.ipv4.isValid()) {
            standard_metadata.egress_spec = 0;
        }
    }
}

control MyComputeChecksum(headers hdr, bool verifyChecksum) {
    apply {
        // Add your code here
    }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyComputeChecksum(), MyDeparser()) main;