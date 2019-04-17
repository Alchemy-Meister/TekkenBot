from enum import Enum

class AttackType(Enum):
    ANTIAIR_ONLY = 11 #Doesn't hit characters on the ground? Very rare, appears on Alisa's chainsaw stance f+2
    THROW = 10  #this is only the attack type *during* the throw animation
    LOW_UNBLOCKABLE = 9 #Yoshimitsu's 10 hit combo 2 has one
    HIGH_UNBLOCKABLE = 8  #Akuma's focus attack
    MID_UNBLOCKABLE = 7
    #UNKNOWN_6 = 6 #????? may not exist
    HIGH = 5
    SMID = 4
    PROJ = 3 #Special mids that can't be parried. Unknown if/what other properties they share.
    MID = 2
    LOW = 1
    NA = 0 #This move is not an attack


class SimpleMoveStates(Enum):
    UNINITIALIZED = 0

    STANDING_FORWARD = 1
    STANDING_BACK = 2
    STANDING = 3
    STEVE = 4 #steve?



    CROUCH_FORWARD = 5
    CROUCH_BACK = 6
    CROUCH = 7

    UNKNOWN_TYPE_9 = 9 #seen on Ling

    GROUND_FACEUP = 12
    GROUND_FACEDOWN = 13

    JUGGLED = 14
    KNOCKDOWN = 15

    #THE UNDERSTANDING OF THE FOLLOWING VALUES IS NOT COMPLETE

    OFF_AXIS_GETUP = 8

    UNKNOWN_10 = 10 #Yoshimitsu
    UNKNOWN_GETUP_11 = 11

    WALL_SPLAT_18 = 18
    WALL_SPLAT_19 = 19
    TECH_ROLL_OR_FLOOR_BREAK = 20

    UNKNOWN_23 = 23 #Kuma

    AIRBORNE_24 = 24 #Yoshimitsu
    AIRBORNE = 25
    AIRBORNE_26 = 26 #Eliza. Chloe
    FLY = 27 #Devil Jin 3+4




class ComplexMoveStates(Enum):  #These are tracking states>
    F_MINUS = 0 # this doubles as the nothing state and an attack_starting state. #occurs on kazuya's hellsweep

    S_PLUS = 1 #homing
    S = 2 #homing, often with screw, seems to more often end up slightly off-axis?
    A = 3 #this move 'realigns' if you pause before throwing it out
    UN04 = 4 # extremely rare, eliza ff+4, 2 has this
    C_MINUS = 5 # realigns either slightly worse or slightly better than C, hard to tell
    A_PLUS = 6 #realigns very well #Alisa's b+2, 1 has this, extremely rare
    C = 7 #this realigns worse than 'A'

    END1 = 10 #after startup  ###Kazuya's ff+3 doesn't have a startup or attack ending flag, it's just 0 the whole way through ???  ###Lili's d/b+4 doesn't have it after being blocked
    BLOCK = 11
    WALK = 12 #applies to dashing and walking
    SIDEROLL_GETUP = 13 #only happens after side rolling???
    SIDEROLL_STAYDOWN = 14
    SS = 15 #sidestep left or right, also applies to juggle techs


    RECOVERING = 16 #happens after you stop walking forward or backward, jumping, getting hit, going into a stance, and some other places
    UN17 = 17  # f+4 with Ling
    UN18 = 18 #King's 1+2+3+4 ki charge

    UN20 = 20 #Dragunov's d+3+4 ground stomp

    UN22 = 22 #Eddy move
    UN23 = 23 #Steve 3+4, 1

    SW = 28 #sidewalk left or right


    UNKN = 999999 #used to indicate a non standard tracking move

class ThrowTechs(Enum):
    NONE = 0
    TE1 = 1 #both 1 and 2 seem to sometimes include normal throws that can be broken with either
    TE2 = 2
    TE1_2 = 3

class StunStates(Enum):
    NONE = 0
    UNKNOWN_2 = 2 #Lili BT/Jumping/Kicks?
    BLOCK = 0x01000100
    GETTING_HIT = 0x100
    DOING_THE_HITTING = 0x10000
    BEING_PUNISHED = 0x10100 #One frame at the begining of a punish #Also appears during simultaneous couterhits

    BLOCK_NO_HIT = 0x1000000 #law's UF+4, sometimes???? Proximity guard maybe?

class RawCancelStates(Enum):
    STUCK = 0 #Pressing buttons doesn't do anything
    UNKNOWN_1 = 1 #1 frames occurs during Alisa's u/f 1+2 command grab, also occurs during asuka's parry escapes
    CANCELABLE = 0x00010000
    BUFFERABLE = 0x01010000 #coming out of attack for sure, probably block and hit stun too?
    UNKNOWN_2 = 2 #Alisa's d+3 and chainsaw stance moves cause this, maybe it's a conditional buffer?  Also triggers during normal throws
    MOVE_ENDING_1 = 0x00010001  # ??? 3 frames at the end of cancel window??? alisa d+2
    MOVE_ENDING_2 = 0x00010002 #??? 1 frames near the end (or at the end?) of cancelable moves
    #Theory: 1 and 2 refer to 'parryable' states, these include the active frames of moves and the throw tech windows of moves
    # the next bit is the cancelable/not cancelable bit and finally there's a 'is being buffered' bit
    #EDIT: Doesn't seem to be parryyable state. Mostly correspond to active frames, but not entirely.

class CancelStatesBitmask(Enum):
    CANCELABLE =  0x00010000
    BUFFERABLE =  0x01000000
    PARRYABLE_1 = 0x00000001
    PARRYABLE_2 = 0x00000002


#Note that this information resides on the player BEING hit not the player doing the hitting. Also note that there's no counter hit state for side or back attacks.
class HitOutcome(Enum):
    NONE = 0
    BLOCKED_STANDING = 1
    BLOCKED_CROUCHING = 2
    JUGGLE = 3
    SCREW = 4
    UNKNOWN_SCREW_5 = 5 #Xiaoyu's sample combo 3 ends with this, off-axis or right side maybe?
    UNKNOWN_6 = 6 #May not exist???
    UNKNOWN_SCREW_7 = 7 #Xiaoy's sample combo 3 includes this
    GROUNDED_FACE_DOWN= 8
    GROUNDED_FACE_UP = 9
    COUNTER_HIT_STANDING = 10
    COUNTER_HIT_CROUCHING = 11
    NORMAL_HIT_STANDING = 12
    NORMAL_HIT_CROUCHING = 13
    NORMAL_HIT_STANDING_LEFT = 14
    NORMAL_HIT_CROUCHING_LEFT = 15
    NORMAL_HIT_STANDING_BACK = 16
    NORMAL_HIT_CROUCHING_BACK = 17
    NORMAL_HIT_STANDING_RIGHT = 18
    NORMAL_HIT_CROUCHING_RIGHT = 19


class JumpFlagBitmask(Enum):
    #GROUND = 0x800000
    #LANDING_OR_STANDING = 0x810000
    JUMP = 0x820000

class InputDirectionCodes(Enum):
    NULL = 0

    N = 0x20

    u = 0x100
    ub = 0x80
    uf = 0x200

    f = 0x40
    b = 0x10

    d = 4
    df = 8
    db = 2

class InputAttackCodes(Enum):
    N = 0
    x1 = 512
    x2 = 1024
    x3 = 2048
    x4 = 4096
    x1x2 = 1536
    x1x3 = 2560
    x1x4 = 4608
    x2x3 = 3072
    x2x4 = 5120
    x3x4 = 6144
    x1x2x3 = 3584
    x1x2x4 = 5632
    x1x3x4 = 6656
    x2x3x4 = 7168
    x1x2x3x4 = 7680
    xRAGE = 8192

class CharacterCodes(Enum):
    PAUL = 0
    LAW = 1
    KING = 2
    YOSHIMITSU = 3
    HWOARANG = 4
    XIAOYU = 5
    JIN = 6
    BRYAN = 7
    HEIHACHI = 8
    KAZUYA = 9
    STEVE = 10
    JACK_7 = 11
    ASUKA = 12
    DEVIL_JIN = 13
    FENG = 14
    LILI = 15
    DRAGUNOV = 16
    LEO = 17
    LARS = 18
    ALISA = 19
    CLAUDIO = 20
    KATARINA = 21
    LUCKY_CHLOE = 22
    SHAHEEN = 23
    JOSIE = 24
    GIGAS = 25
    KAZUMI = 26
    DEVIL_KAZUMI = 27 #not selectable
    NINA = 28
    MASTER_RAVEN = 29
    LEE = 30
    BOB = 31
    AKUMA = 32
    KUMA = 33
    PANDA = 34
    EDDY = 35
    ELIZA = 36
    MIGUEL = 37

    NOT_YET_LOADED = 71 #value when a match starts for (??) frames until char_id loads

    NO_SELECTION = 255 #value if cursor is not shown

class UniversalAnimationCodes(Enum):
    NEUTRAL = 32769
    CROUCHING_NEUTRAL = 32770
