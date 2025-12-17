import { BASEURL } from "./base";


export const LoginSocial = async (
    provider: string, 
    error?: boolean,
    errorMsg?: String,
    ) => {
    const response = await fetch(
        `${BASEURL}/social/${provider}/login/`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        }
    );
    const data = await response.json()
    if (!response.ok){
        error = true;
        errorMsg = data.non_field_errors[0]
        return
    }
    window.location.href = data.authentication_url
}