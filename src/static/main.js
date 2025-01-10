
document.addEventListener("DOMContentLoaded", function(){
    
    if (localStorage.getItem("token") === undefined){
        this.location.href = "/login/"
    }else if (!localStorage.getItem("token")){
        this.location.pathname = "/login/"
    }
    
    if (location.pathname === "/"){
        fetch(`${this.location.origin}/api/user/`, {
            method: "GET",
            headers: {
                "Authorization": `token ${localStorage.getItem("token")}`
            }
        }).then(response=> response.json())
        .then(data=> document.querySelector("#result").innerHTML = data["username"]) 
    }
    
})