from dataclasses import dataclass

@dataclass
class RegisterFieldRep:
    '''the representation of a register field'''
    name: str
    nameDesc: str
    bitMSB: int
    bitLSB: int
    desc: str
    isReserved: bool # keep?
    isWriteable: bool
    isReadable: bool
    resetVal: int # keep??? 不保留 和 RegisterRep.resetVal 重复

@dataclass
class RegisterAddressRep:
    '''the representation of register address'''
    abs: int # absolute address
    base: int # absolute address = base address + offset
    offset: int # absolute address = base address + offset

@dataclass
class RegisterRep:
    '''the representation of a register'''
    name: str # or short name
    nameDesc: str # or long name
    bitLen: int
    resetVal: int
    fieldTable: list[RegisterFieldRep]
    addrInfo: RegisterAddressRep
