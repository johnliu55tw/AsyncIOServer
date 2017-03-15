def Checksum(packet):
    chksum = 0
    for b in packet:
        chksum ^= b
    return bytes([chksum])


def HasValidChecksum(packet):
    chksum = bytes([packet[-1]])
    return Checksum(packet[:-1]) == chksum


def FindValidPackets(buffer, header, length=None, lengthIndex=None,
                     lengthOffset=0, ChksumIncludeHeader=True):
    """Looking for valid data packet in the given data.

    Args:
        buffer (bytes): The data.
        header (bytes): The header of the packet.
        length (int): The length of the packet.
            User could pass this argument to define the packet length if
            it's consistent for all the packet. If the length of the packet
            is inconsistent and defined by the data packet itself (through
            some certain field in the packet), user could defines it by
            the lengthIndex argument. Notice that either length or
            lengthIndex must be passed. If both were passed, the length
            will override the lengthIndex.
        lengthIndex (int): The index of the length information in the packet.
            User could pass this argument to define the packet length if
            the length information is self-contained by the packet.
        lengthOffset (int): The offset which will be added to the length.
            Sometimes the length information provided by the packet itself
            will be different from the real packet length. For instance, the
            length information may not include the header and checksum.
            Since this function requires total length to be working, user
            could use this argument to increase the length information
            provided by the packet inself. Notice this won't work when the
            length information is provided by the length argument.
        ChksumIncludeHeader (bool): Define if the header is included in
            checksum calculation.
            Sometimes the calculation of checksum excludes the header. User
            could use this argument to defined this.

    Returns:
        checkedPacketList (list of bytes): Valid packet list.
        remainedPacket (bytes): remained data byte
        """
    if length is None and lengthIndex is None:
        raise ValueError("Either length or lengthIndex must be set")
    if len(header) == 0:
        raise ValueError("header must be set")
    bufferLength = len(buffer)

    checkedPacketList = list()
    headerIndexList = list()
    remainedPacket = bytes()

    foundLength = 0
    headerIndex = 0
    while True:
        # Locate the first header in buffer
        headerIndex = buffer.find(header[0], headerIndex)
        if headerIndex < 0:
            break
        # Make sure the length of buffer is able to do the comparison
        if (bufferLength - headerIndex) < len(header):
            remainedPacket += buffer[headerIndex:]
            break
        # Find the rest of the header
        if buffer[headerIndex:].startswith(header) is False:
            # Skip to the next
            headerIndex += 1
            continue
        # Test the remained buffer length
        if length is not None:
            if (bufferLength - headerIndex) < length:
                remainedPacket += buffer[headerIndex:]
                break
            foundLength = length
        else:
            # remained buffer length is less than the lengthIndex
            if (bufferLength - headerIndex) < (lengthIndex + 1):
                remainedPacket += buffer[headerIndex:]
                break
            if (bufferLength - headerIndex) <\
               (buffer[headerIndex+lengthIndex]+lengthOffset):
                remainedPacket += buffer[headerIndex:]
                break
            foundLength = buffer[headerIndex+lengthIndex]+lengthOffset
        # Check the checksum
        if ChksumIncludeHeader:
            if HasValidChecksum(
                    buffer[headerIndex:headerIndex+foundLength]) is False:
                headerIndex += 1
                continue
        else:
            if HasValidChecksum(
                    buffer[headerIndex+len(header):headerIndex+foundLength]) is False:
                headerIndex += 1
                continue
        # Pass every examination
        checkedPacketList.append(buffer[headerIndex:headerIndex+foundLength])
        headerIndexList.append(headerIndex)
        headerIndex += foundLength

    return (checkedPacketList, remainedPacket)
