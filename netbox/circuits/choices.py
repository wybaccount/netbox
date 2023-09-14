from utilities.choices import ChoiceSet


#
# Circuits
#

class CircuitStatusChoices(ChoiceSet):
    key = 'Circuit.status'

    STATUS_DEPROVISIONING = 'deprovisioning'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_PROVISIONING = 'provisioning'
    STATUS_OFFLINE = 'offline'
    STATUS_DECOMMISSIONED = 'decommissioned'

    CHOICES = [
        (STATUS_PLANNED, '规划中', 'cyan'),
        (STATUS_PROVISIONING, '资源分配', 'blue'),
        (STATUS_ACTIVE, '运行中', 'green'),
        (STATUS_OFFLINE, '离线', 'red'),
        (STATUS_DEPROVISIONING, '资源回收', 'yellow'),
        (STATUS_DECOMMISSIONED, '退役', 'gray'),
    ]


class CircuitCommitRateChoices(ChoiceSet):
    key = 'Circuit.commit_rate'

    CHOICES = [
        (10000, '10 Mbps'),
        (100000, '100 Mbps'),
        (1000000, '1 Gbps'),
        (10000000, '10 Gbps'),
        (25000000, '25 Gbps'),
        (40000000, '40 Gbps'),
        (100000000, '100 Gbps'),
        (1544, 'T1 (1.544 Mbps)'),
        (2048, 'E1 (2.048 Mbps)'),
    ]


#
# CircuitTerminations
#

class CircuitTerminationSideChoices(ChoiceSet):

    SIDE_A = 'A'
    SIDE_Z = 'Z'

    CHOICES = (
        (SIDE_A, 'A'),
        (SIDE_Z, 'Z')
    )


class CircuitTerminationPortSpeedChoices(ChoiceSet):
    key = 'CircuitTermination.port_speed'

    CHOICES = [
        (10000, '10 Mbps'),
        (100000, '100 Mbps'),
        (1000000, '1 Gbps'),
        (10000000, '10 Gbps'),
        (25000000, '25 Gbps'),
        (40000000, '40 Gbps'),
        (100000000, '100 Gbps'),
        (1544, 'T1 (1.544 Mbps)'),
        (2048, 'E1 (2.048 Mbps)'),
    ]
