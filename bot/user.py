def get_fullname(message):

    user_name = message.from_user.first_name  
    user_lastname = message.from_user.last_name

    if user_name and user_lastname:
        full_name = f"{user_name} {user_lastname}"
    elif user_name:
        full_name = user_name
    else:
        full_name = "Пользователь"

    return full_name
