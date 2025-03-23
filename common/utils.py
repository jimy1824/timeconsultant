def update_type(instances, instance_type):
    for instance in instances:
        instance['type'] = instance_type
    return list(instances)
