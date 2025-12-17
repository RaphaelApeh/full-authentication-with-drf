
export type MessageResponse = {
    message?: String
}

export type User = {
    username?: String
    email?: String
    access_token?: String
    refresh_token?: String
}

export type UserRegister = {
    username: String
    email: String
    password: String
    password2: String
}

export type UserLogin = {
    username: String
    password: String
}