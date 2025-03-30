#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

struct Headers {
    ethernet_t ethernet;
}

struct Meta {
}

parser MyParser(packet_in packet, out Headers hdr, inout Meta meta, inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition accept;
    }
}

control MyIngress(inout Headers hdr, inout Meta meta, inout standard_metadata_t standard_metadata) {
    apply {
    }
}

control MyEgress(inout Headers hdr, inout Meta meta, inout standard_metadata_t standard_metadata) {
    apply {
    }
}

control MyDeparser(packet_out packet, in Headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
    }
}

control MyVerifyChecksum(inout Headers hdr, inout Meta meta) {
    apply {
    }
}

control MyUpdateChecksum(inout Headers hdr, inout Meta meta) {
    apply {
    }
}

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyUpdateChecksum(),
    MyDeparser()
) main;