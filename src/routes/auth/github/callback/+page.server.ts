import { redirect } from "@sveltejs/kit";

export let load: any = async  ({ url, fetch, cookies }: any) => {

    const code = url.searchParams.get("code")
    const state = url.searchParams.get("state")

    if (!code || !state) throw redirect(303, "/login")
    const response = await fetch(
        `http://127.0.0.1:8000/api/login/github/callback/?code=${code}?state=${state}`,
        {
            method: "GET",
            credentials: "include",
        }
    )
    if (!response.ok) throw redirect(303, "/login")
    const data = await response.json()
    console.log(data)
    return data;
    
}