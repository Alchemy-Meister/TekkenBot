from enum import Enum

class AttackType(Enum):
    """

    """
    # Doesn't hit characters on the ground?
    # Very rare, appears on Alisa's chainsaw stance f+2
    ANTIAIR_ONLY = 11
    THROW = 10  # This is only the attack type *during* the throw animation
    LOW_UNBLOCKABLE = 9 # Yoshimitsu's 10 hit combo 2 has one
    HIGH_UNBLOCKABLE = 8  # Akuma's focus attack
    MID_UNBLOCKABLE = 7
    # UNKNOWN_6 = 6 # ????? may not exist
    HIGH = 5
    SMID = 4
    # Special mids that can't be parried.
    # Unknown if/what other properties they share.
    PROJ = 3
    MID = 2
    LOW = 1
    NA = 0 # This move is not an attack


class SimpleMoveStates(Enum):
    """

    """
    UNINITIALIZED = 0

    STANDING_FORWARD = 1
    STANDING_BACK = 2
    STANDING = 3
    STEVE = 4 # steve?



    CROUCH_FORWARD = 5
    CROUCH_BACK = 6
    CROUCH = 7

    UNKNOWN_TYPE_9 = 9 # Seen on Ling

    GROUND_FACEUP = 12
    GROUND_FACEDOWN = 13

    JUGGLED = 14
    KNOCKDOWN = 15

    # THE UNDERSTANDING OF THE FOLLOWING VALUES IS NOT COMPLETE

    OFF_AXIS_GETUP = 8

    UNKNOWN_10 = 10 # Yoshimitsu
    UNKNOWN_GETUP_11 = 11

    WALL_SPLAT_18 = 18
    WALL_SPLAT_19 = 19
    TECH_ROLL_OR_FLOOR_BREAK = 20

    UNKNOWN_23 = 23 # Kuma

    AIRBORNE_24 = 24 # Yoshimitsu
    AIRBORNE = 25
    AIRBORNE_26 = 26 # Eliza, Chloe
    FLY = 27 # Devil Jin 3+4




class ComplexMoveStates(Enum):
    """
    These are tracking states>
    """
    # This doubles as the nothing state and an attack_starting state.
    # Occurs on kazuya's hellsweep
    F_MINUS = 0

    S_PLUS = 1 # Homing
    # Homing, often with screw, seems to more often end up slightly off-axis?
    S = 2
    A = 3 # This move 'realigns' if you pause before throwing it out
    UN04 = 4 # Extremely rare, eliza ff+4, 2 has this
    # Realigns either slightly worse or slightly better than C, hard to tell
    C_MINUS = 5
    A_PLUS = 6 # Realigns very well. Alisa's b+2, 1 has this, extremely rare
    C = 7 # This realigns worse than 'A'

    # After startup
    #   Kazuya's ff+3 doesn't have a startup or attack ending flag,
    #       it's just 0 the whole way through ???
    #   Lili's d/b+4 doesn't have it after being blocked
    END1 = 10
    BLOCK = 11
    WALK = 12 # Applies to dashing and walking
    SIDEROLL_GETUP = 13 # Only happens after side rolling???
    SIDEROLL_STAYDOWN = 14
    SS = 15 # Sidestep left or right, also applies to juggle techs

    # Happens after you stop walking forward or backward, jumping, getting hit,
    # going into a stance, and some other places
    RECOVERING = 16
    UN17 = 17  # f+4 with Ling
    UN18 = 18 # King's 1+2+3+4 ki charge

    UN20 = 20 # Dragunov's d+3+4 ground stomp

    UN22 = 22 # Eddy move
    UN23 = 23 # Steve 3+4, 1

    SW = 28 # Sidewalk left or right


    UNKN = 999999 # Used to indicate a non standard tracking move

class ThrowTechs(Enum):
    NONE = 0
    # Both, 1 and 2 seem to sometimes include normal throws that can be broken
    # with either
    TE1 = 1
    TE2 = 2
    TE1_2 = 3

class StunStates(Enum):
    NONE = 0
    UNKNOWN_2 = 2 # Lili BT/Jumping/Kicks?
    BLOCK = 0x01000100
    GETTING_HIT = 0x100
    DOING_THE_HITTING = 0x10000
    # One frame at the begining of a punish #Also appears during simultaneous
    # couterhits
    BEING_PUNISHED = 0x10100

    BLOCK_NO_HIT = 0x1000000 # Law's UF+4, sometimes???? Proximity guard maybe?

class RawCancelStates(Enum):
    STUCK = 0 # Pressing buttons doesn't do anything
    # 1 frame occurs during Alisa's u/f 1+2 command grab, also occurs during
    # Asuka's parry escapes
    UNKNOWN_1 = 1
    CANCELABLE = 0x00010000
    # Coming out of attack for sure, probably block and hit stun too?
    BUFFERABLE = 0x01010000
    # Alisa's d+3 and chainsaw stance moves cause this, maybe it's a conditional
    # buffer?  Also triggers during normal throws
    UNKNOWN_2 = 2
    # ??? 3 frames at the end of cancel window??? Alisa d+2
    MOVE_ENDING_1 = 0x00010001
    #??? 1 frame near the end (or at the end?) of cancelable moves
    MOVE_ENDING_2 = 0x00010002
    # Theory: 1 and 2 refer to 'parryable' states, these include the active
    #   frames of moves and the throw tech windows of moves
    # the next bit is the cancelable/not cancelable bit and finally there's a
    #   'is being buffered' bit
    # EDIT: Doesn't seem to be parryyable state. Mostly correspond to active
    # frames, but not entirely.

class CancelStatesBitmask(Enum):
    CANCELABLE = 0x00010000
    BUFFERABLE = 0x01000000
    PARRYABLE_1 = 0x00000001
    PARRYABLE_2 = 0x00000002

class HitOutcome(Enum):
    """
    # Note that this information resides on the player BEING hit not the player
    # doing the hitting. Also note that there's no counter hit state for side or
    # back attacks.
    """
    NONE = 0
    BLOCKED_STANDING = 1
    BLOCKED_CROUCHING = 2
    JUGGLE = 3
    SCREW = 4
    # Xiaoyu's sample combo 3 ends with this, off-axis or right side maybe?
    UNKNOWN_SCREW_5 = 5
    UNKNOWN_6 = 6 # May not exist???
    UNKNOWN_SCREW_7 = 7 # Xiaoyu's sample combo 3 includes this
    GROUNDED_FACE_DOWN = 8
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
    # GROUND = 0x800000
    # LANDING_OR_STANDING = 0x810000
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
    DEVIL_KAZUMI = 27 # Not selectable
    NINA = 28
    MASTER_RAVEN = 29
    LEE = 30
    BOB = 31
    AKUMA = 32
    KUMA = 33
    PANDA = 34
    EDDY = 35
    ELIZA = 36 # DLC
    MIGUEL = 37
    TEKKEN_FORCE = 38 # Not selectable
    KID_KAZUYA = 39 # Not selectable
    JACK_4 = 40 # Not selectable
    YOUNG_HEIHACHI = 41 # Not selectable
    GEESE = 43 # DLC
    TRAINING_DUMMY = 42 # Not selectable
    NOCTIS = 44 # DLC
    LEI = 46 # DLC
    MARDUK = 47 # DLC
    NEGAN = 50 # DLC

    # Value when a match starts for (??) frames until char_id loads
    NOT_YET_LOADED = 71

    NO_SELECTION = 255 # Value if cursor is not shown

class StageIDs(Enum):
    """

    """
    MISHIMA_DOJO = 0
    FORGOTTEN_REALM = 1
    JUNGLE_OUTPOST = 2
    ARCTIC_SNOWFALL = 3
    TWILIGHT_CONFLICT = 4
    DRAGON_NEST = 5
    SOUQ = 6
    DEVILS_PIT = 7
    MISHIMA_BUILDING = 8
    ABANDONED_TEMPLE = 9
    DUOMO_DI_SIRIO = 30
    ARENA = 31
    G_CORP_HELIPAD = 32
    G_CORP_HELIPAD_NIGHT = 33
    BRIMSTONE_AND_FIRE = 35
    PRECIPICE_OF_FATE = 36
    VIOLET_SYSTEMS = 37
    KINDER_GYM = 39
    INFINITE_AZURE = 40
    GEOMETRIC_PLANE = 41
    WARM_UP = 42 # Not selectable
    HOWARD_ESTATE = 51
    HAMMERHEAD = 52
    JUNGLE_OUTPOST_2 = 53
    TWILIGHT_CONFLICT_2 = 54
    INFINITE_AZURE_2 = 55
    LAST_DAY_ON_EARTH = 56 # DLC

class MainMenuIDs(Enum):
    """

    """
    STORY = 0
    ONLINE = 1
    OFFLINE = 2
    CUSTOMIZATION = 3
    GALLERY = 5
    OPTIONS = 6
    PLAYER_INFORMATION = 7
    STORE = 8
    ULTIMATE_TEKKEN_BOWL = 10
    QUIT = 11

class OfflineMainMenuIDs(Enum):
    """

    """
    ARCADE_BATTLE = 0
    TREASURE_BATTLE = 1
    VS_BATTLE = 2
    PRACTICE = 3

class UniversalAnimationCodes(Enum):
    NEUTRAL = 32769
    CROUCHING_NEUTRAL = 32770
