def helper_adsb_bin2hex(b):
    """
    Converts a binary numeric array to a hexadecimal character array.

    Parameters:
    b (list of int): Binary numeric array (column vector) where the number of elements
                     must be a multiple of four.

    Returns:
    str: Hexadecimal character array.
    """
    if b is not None:
        if len(b) % 4 != 0:
            raise ValueError("The length of the binary array must be a multiple of four.")
        else:
            num_hex_symbols = len(b) // 4
            hex_symbols = '0123456789ABCDEF'
            h = []

            for i in range(num_hex_symbols):
                idx = i * 4
                bin_value = b[idx:idx + 4]
                hex_value = hex_symbols[bin_value[0] * 8 + bin_value[1] * 4 + bin_value[2] * 2 + bin_value[3] * 1]
                h.append(hex_value)

            return ''.join(h)
    else:
        return None