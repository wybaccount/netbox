from utilities.choices import ChoiceSet


class IPAddressFamilyChoices(ChoiceSet):

    FAMILY_4 = 4
    FAMILY_6 = 6

    CHOICES = (
        (FAMILY_4, 'IPv4'),
        (FAMILY_6, 'IPv6'),
    )


#
# Prefixes
#

class PrefixStatusChoices(ChoiceSet):
    key = 'Prefix.status'

    STATUS_CONTAINER = 'container'
    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_CONTAINER, '容器', 'gray'),
        (STATUS_ACTIVE, '活动', 'blue'),
        (STATUS_RESERVED, '保留', 'cyan'),
        (STATUS_DEPRECATED, '已废弃', 'red'),
    ]


#
# IP Ranges
#

class IPRangeStatusChoices(ChoiceSet):
    key = 'IPRange.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, '活动', 'blue'),
        (STATUS_RESERVED, '保留', 'cyan'),
        (STATUS_DEPRECATED, '已废弃', 'red'),
    ]


#
# IP Addresses
#

class IPAddressStatusChoices(ChoiceSet):
    key = 'IPAddress.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'
    STATUS_DHCP = 'dhcp'
    STATUS_SLAAC = 'slaac'

    CHOICES = [
        (STATUS_ACTIVE, '运行中', 'blue'),
        (STATUS_RESERVED, '保留', 'cyan'),
        (STATUS_DEPRECATED, '已废弃', 'red'),
        (STATUS_DHCP, 'DHCP', 'green'),
        (STATUS_SLAAC, 'SLAAC', 'purple'),
    ]


class IPAddressRoleChoices(ChoiceSet):

    ROLE_LOOPBACK = 'loopback'
    ROLE_SECONDARY = 'secondary'
    ROLE_ANYCAST = 'anycast'
    ROLE_VIP = 'vip'
    ROLE_VRRP = 'vrrp'
    ROLE_HSRP = 'hsrp'
    ROLE_GLBP = 'glbp'
    ROLE_CARP = 'carp'

    CHOICES = (
        (ROLE_LOOPBACK, '环回地址', 'gray'),
        (ROLE_SECONDARY, '次要地址', 'blue'),
        (ROLE_ANYCAST, '任播地址', 'yellow'),
        (ROLE_VIP, '虚拟IP地址', 'purple'),
        (ROLE_VRRP, '虚拟路由冗余协议', 'green'),
        (ROLE_HSRP, '热备份路由协议', 'green'),
        (ROLE_GLBP, '网关负载均衡协议', 'green'),
        (ROLE_CARP, '公共地址冗余协议', 'green'),
    )


#
# FHRP
#

class FHRPGroupProtocolChoices(ChoiceSet):

    PROTOCOL_VRRP2 = 'vrrp2'
    PROTOCOL_VRRP3 = 'vrrp3'
    PROTOCOL_HSRP = 'hsrp'
    PROTOCOL_GLBP = 'glbp'
    PROTOCOL_CARP = 'carp'
    PROTOCOL_CLUSTERXL = 'clusterxl'
    PROTOCOL_OTHER = 'other'

    CHOICES = (
        ('Standard', (
            (PROTOCOL_VRRP2, 'VRRPv2'),
            (PROTOCOL_VRRP3, 'VRRPv3'),
            (PROTOCOL_CARP, 'CARP'),
        )),
        ('CheckPoint', (
            (PROTOCOL_CLUSTERXL, 'ClusterXL'),
        )),
        ('Cisco', (
            (PROTOCOL_HSRP, 'HSRP'),
            (PROTOCOL_GLBP, 'GLBP'),
        )),
        (PROTOCOL_OTHER, 'Other'),
    )


class FHRPGroupAuthTypeChoices(ChoiceSet):

    AUTHENTICATION_PLAINTEXT = 'plaintext'
    AUTHENTICATION_MD5 = 'md5'

    CHOICES = (
        (AUTHENTICATION_PLAINTEXT, 'Plaintext'),
        (AUTHENTICATION_MD5, 'MD5'),
    )


#
# VLANs
#

class VLANStatusChoices(ChoiceSet):
    key = 'VLAN.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, '活动', 'blue'),
        (STATUS_RESERVED, '保留', 'cyan'),
        (STATUS_DEPRECATED, '已废弃', 'red'),
    ]


#
# Services
#

class ServiceProtocolChoices(ChoiceSet):

    PROTOCOL_TCP = 'tcp'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_SCTP = 'sctp'

    CHOICES = (
        (PROTOCOL_TCP, 'TCP'),
        (PROTOCOL_UDP, 'UDP'),
        (PROTOCOL_SCTP, 'SCTP'),
    )


class L2VPNTypeChoices(ChoiceSet):
    TYPE_VPLS = 'vpls'
    TYPE_VPWS = 'vpws'
    TYPE_EPL = 'epl'
    TYPE_EVPL = 'evpl'
    TYPE_EPLAN = 'ep-lan'
    TYPE_EVPLAN = 'evp-lan'
    TYPE_EPTREE = 'ep-tree'
    TYPE_EVPTREE = 'evp-tree'
    TYPE_VXLAN = 'vxlan'
    TYPE_VXLAN_EVPN = 'vxlan-evpn'
    TYPE_MPLS_EVPN = 'mpls-evpn'
    TYPE_PBB_EVPN = 'pbb-evpn'

    CHOICES = (
        ('VPLS', (
            (TYPE_VPWS, 'VPWS'),
            (TYPE_VPLS, 'VPLS'),
        )),
        ('VXLAN', (
            (TYPE_VXLAN, 'VXLAN'),
            (TYPE_VXLAN_EVPN, 'VXLAN-EVPN'),
        )),
        ('L2VPN E-VPN', (
            (TYPE_MPLS_EVPN, 'MPLS EVPN'),
            (TYPE_PBB_EVPN, 'PBB EVPN'),
        )),
        ('E-Line', (
            (TYPE_EPL, 'EPL'),
            (TYPE_EVPL, 'EVPL'),
        )),
        ('E-LAN', (
            (TYPE_EPLAN, 'Ethernet Private LAN'),
            (TYPE_EVPLAN, 'Ethernet Virtual Private LAN'),
        )),
        ('E-Tree', (
            (TYPE_EPTREE, 'Ethernet Private Tree'),
            (TYPE_EVPTREE, 'Ethernet Virtual Private Tree'),
        )),
    )

    P2P = (
        TYPE_VPWS,
        TYPE_EPL,
        TYPE_EPLAN,
        TYPE_EPTREE
    )
