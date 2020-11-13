import discord

def get_rolemap(guild: discord.Guild):
    return dict((role.id, role) for role in guild.roles)

def get_add_remove(user_role_ids: list, ctf_role_ids: list, desired_user_ids: list, rolemap: dict):
    user_role_ids, ctf_role_ids, desired_user_ids = set(user_role_ids), set(ctf_role_ids), set(desired_user_ids)

    current_valid = user_role_ids & ctf_role_ids

    to_add = desired_user_ids - current_valid
    to_rem = current_valid - desired_user_ids

    to_add = [rolemap[r] for r in to_add]
    to_rem = [rolemap[r] for r in to_rem]

    return (to_add, to_rem)