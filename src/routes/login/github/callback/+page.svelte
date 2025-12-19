<script>
    import { BASEURL } from "$lib/helpers/base";
    import { goto } from "$app/navigation";

    const urlString = window.location.search;
    const params = new URLSearchParams(urlString);
    const code = params.get("code");
    const state = params.get("state");

    const callback = async () => {
        const response = await fetch(
            `${BASEURL}/social/github/callback/`,
            {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "GET",
                body: JSON.stringify({code: code, state: state})
            }
        )
        if (!response.ok){

        }
        const data = await response.json();
        localStorage.setItem("access_token", data.access_token)
        localStorage.setItem("refresh_token", data.refresh_token)

        await goto("/")
    }
    window.addEventListener("load", callback)
</script>
<h1>Redirecting ....</h1>