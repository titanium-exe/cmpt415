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

typedef bit<32> PacketCounter_t;
typedef bit<9>  RegisterIndex_t;

extern Register<T, S> {
    T    read  (S index);
    void write (S index, T value);
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

control MyIngress(inout headers hdr, inout standard_metadata_t standard_metadata, 
                  Register<PacketCounter_t, RegisterIndex_t> ipv4_packet_count) {
    action count_ipv4_packets() {
        PacketCounter_t packet_count = ipv4_packet_count.read((RegisterIndex_t)0);
        packet_count = packet_count + 1;
        ipv4_packet_count.write((RegisterIndex_t)0, packet_count);
    }

    table count_ipv4_packets_table {
        key = { hdr.ipv4.version : exact; }
        actions = { count_ipv4_packets; }
        default_action = count_ipv4_packets();
    }

    apply {
        if (hdr.ipv4.isValid()) {
            count_ipv4_packets_table.apply();
        }
    }
}

control MyEgress(inout headers hdr, inout standard_metadata_t standard_metadata) {
    apply { }
}

control MyDeparser(packet_out packet, inout headers hdr) {
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