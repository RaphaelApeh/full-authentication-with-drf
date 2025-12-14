import { redirect, fail } from '@sveltejs/kit';

export let actions = {
    default: async function({ request }: any){
        let errorMsg;
        const data = await request.formData();
        const username = data.get("username");
        const email = data.get("email");
        const password1 = data.get("password");
        let form = new FormData()
        form.set("username", username);
        form.set("email", email);
        form.set("password1", password1);
        const response = await fetch("http://127.0.0.1:8000/api/register/",
            {
                method: "POST",
                body: JSON.stringify(form),
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )
        if (!response.ok){
            throw fail(403, response)
        }
        const message = response.json();

        return {
            //@ts-ignore
            success: message.message
        }

    }
}