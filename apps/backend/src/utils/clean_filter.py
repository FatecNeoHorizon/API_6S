def clean_filter(filter_dict):
    if not isinstance(filter_dict, dict):
        return filter_dict
    cleaned_filter = {
        k: clean_filter(v) for k, v in filter_dict.items() 
        if v is not None and (not isinstance(v, dict) or len(v) > 0)
    }
    return cleaned_filter

def remove_operators_fields(filter_dict,fields_array):
    try:
        for field in fields_array:
                if len(filter_dict[field]) < 1:
                    filter_dict.pop(field)
    except:
        return filter_dict
    return filter_dict