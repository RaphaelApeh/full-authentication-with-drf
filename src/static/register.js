const form = document.querySelector("form")
const username = document.querySelector("#username")
const email = document.querySelector("#email")
const password = document.querySelector("#password")
const password2 = document.querySelector("#password2")

const csrf = document.currentScript.dataset // {{ csrf_token }}

const url = `${location.origin}/api/register/`
console.log(url)

// Redirect authenticated user.
if (localStorage.getItem("token")){
    location.href = "/"
}
// Main function
function getRegisterApi(event){
    const formData = new FormData(form)
    form.addEventListener("submit", (e)=>{
        e.preventDefault()

        formData.append("username", username.value)
        formData.append("email", email.value)
        formData.append("password", password.value)
        formData.append("password2", password2.value)
        
        // fetching data..
        const fetchData = async ()=> {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "ContentType": "application/json",
                    "X-CSRFToken": csrf.csrf
                },
                body: formData
            });
            const result = await response.json()
            console.log(result)
            if(!result["Error"]){
                alert(result["message"])
            }else {
                alert(JSON.stringify(result["Error"]))
            }
        
        }
        fetchData()
    })
}
document.addEventListener("DOMContentLoaded", getRegisterApi)