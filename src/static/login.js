console.log("Connecting...")
const form = document.querySelector("form")
const userInput = document.querySelector("#userInput")
const password = document.querySelector("#password")

const csrf = document.currentScript.dataset

const url = `${location.origin}/api/login/`

document.addEventListener("DOMContentLoaded", (e)=>{
    
    if(localStorage.getItem("token") === undefined){
        console.error("error")
    }else if(localStorage.getItem("token")){
        location.href = "/"
    }
    userInput.oninput = ()=> {console.log(userInput.value)}
})

const LoginUserIn = () => {

    form.addEventListener("submit", (e)=>{
        e.preventDefault()
        if (userInput.value === "" && password.value === ""){
            alert("Can't submit blank form.")
            return
        }
        const formData = new FormData(form)
        formData.append("username", userInput.value)
        formData.append("password", password.value)
        const fetchData = async ()=>{
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "ContentType": "application/json",
                    "X-CSRFToken": csrf.csrf
                },
                body: formData
            })
            const responseData = await response.json()
            console.log(responseData)
            if (!responseData["Error"]){
                localStorage.setItem("token", responseData["token"])
                if (localStorage.getItem("token") === undefined){
                    localStorage.removeItem("token")
                }
                location.href = "/"
            }else {
                console.error(responseData["Error"])
            }
        
        }
        fetchData()
    })
    
}

document.addEventListener("DOMContentLoaded", LoginUserIn)