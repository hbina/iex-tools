import typing

import yaml


def generate_numpy_parser(input_path: str) -> typing.Tuple[str, str, str]:
    yaml_string = open(input_path, 'r')
    definition = yaml.safe_load(yaml_string)
    struct_name = definition['name']
    members = definition['member']

    # build the list of dtype fields.
    dtype_fields = []
    for member in members:
        field_name = member['name']
        field_type = member['type']
        # if a length is specified, create an array field.
        if 'length' in member:
            length = member['length']
            dtype_fields.append(f'    ("{struct_name}__{field_name}", "{field_type}", {length}),')
        else:
            dtype_fields.append(f'    ("{struct_name}__{field_name}", "{field_type}"),')

    # compose the code snippet parts.
    dtype_code = f'dtype__{struct_name} = np.dtype([\n' + "\n".join(dtype_fields) + "\n])"
    itemsize_code = f'itemsize__{struct_name} = dtype__{struct_name}.itemsize'
    parse_function_code = f'''
@numba.njit(cache=False)
def parse__{struct_name}(buffer: np.ndarray):
    if len(buffer) < itemsize__{struct_name}:
        raise StopIteration()
    header = np.frombuffer(buffer[:itemsize__{struct_name}], dtype=dtype__{struct_name})
    remaining = buffer[itemsize__{struct_name}:]
    return header, remaining
'''.strip()

    # combine all parts.
    # full_code = f"{dtype_code}\n\n{itemsize_code}\n\n{parse_function_code}"
    return dtype_code, itemsize_code, parse_function_code


def compute_field_size(field_type: str, length: int = None) -> int:
    # Mapping the numpy type strings to their byte sizes.
    sizes = {
        '<u1': 1,
        '<u2': 2,
        '<u4': 4,
        '<u8': 8,
        '<i1': 1,
        '<i2': 2,
        '<i4': 4,
        '<i8': 8,
    }
    base_size = sizes.get(field_type)
    if base_size is None:
        raise Exception(f"Unknown field type: {field_type}")
    return base_size * length if length is not None else base_size


def generate_rust_struct(input_path: str) -> str:
    """
    Generate a Rust struct and a TryFrom implementation based on the YAML definition.

    The output will look like:

    #[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
    #[repr(C, packed)]
    pub struct IexTransportHeader {
        version: u8,
        reserved: u8,
        message_protocol_id: u16,
        channel_id: u32,
        session_id: u32,
        payload_length: u16,
        message_count: u16,
        stream_offset: u64,
        first_message_seq_num: u64,
        send_ts: u64,
    }

    impl<'a> TryFrom<&'a [u8]> for &'a IexTransportHeader {
        type Error = ValidityError<&'a [u8; 40], IexTransportHeader>;

        fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {
            println!("value:{:#?}", value);
            let buffer: &[u8; 40] = (&value[0..40]).try_into().unwrap();
            let header: Result<&'a IexTransportHeader, _> = try_transmute_ref!(buffer);
            header
        }
    }

    Parameters:
      input_path: Path to the YAML file with the struct definition.
    """
    import yaml

    with open(input_path, 'r') as f:
        definition = yaml.safe_load(f)
    struct_name = definition['name']
    members = definition['member']

    # Build the field definitions for the Rust struct and compute the total size.
    rust_fields = []
    total_size = 0
    for member in members:
        field_name = member['name']
        field_type = member['type']
        if 'length' in member:
            length = member['length']
            field_def = f"    pub {field_name}: {convert_field_type_to_rust_type_arr(field_type, length)},"
            total_size += compute_field_size(field_type, length)
        else:
            field_def = f"    pub {field_name}: {convert_field_type_to_rust_type(field_type)},"
            total_size += compute_field_size(field_type)
        rust_fields.append(field_def)

    fields_code = "\n".join(rust_fields)

    # Create the Rust struct definition.
    struct_def_code = f"""\
#[derive(Debug, KnownLayout, Immutable, FromBytes, IntoBytes)]
#[repr(C, packed)]
pub struct {struct_name} {{
{fields_code}
}}"""

    # Create the TryFrom implementation.
    impl_code = f"""\
impl<'a> TryFrom<&'a [u8]> for &'a {struct_name} {{
    type Error = ();

    fn try_from(value: &'a [u8]) -> Result<Self, Self::Error> {{
        let buffer: &[u8; {total_size}] = (&value[0..{total_size}]).try_into().map_err(|_| ())?;
        let header = try_transmute_ref!(buffer);
        header.map_err(|_| ())
    }}
}}\n"""

    # Combine the struct definition and the implementation.
    rust_code = struct_def_code + "\n\n" + impl_code
    return rust_code


def convert_field_type_to_rust_type(field_type: str) -> str:
    if field_type == '<u1':
        return 'u8'
    elif field_type == '<u2':
        return 'u16'
    elif field_type == '<u4':
        return 'u32'
    elif field_type == '<u8':
        return 'u64'
    elif field_type == '<i1':
        return 'i8'
    elif field_type == '<i2':
        return 'i16'
    elif field_type == '<i4':
        return 'i32'
    elif field_type == '<i8':
        return 'i64'
    else:
        raise Exception("Bad")


def convert_field_type_to_rust_type_arr(field_type: str, field_length: int) -> str:
    rust_field_type = convert_field_type_to_rust_type(field_type)
    return f"[{rust_field_type}; {field_length}]"
