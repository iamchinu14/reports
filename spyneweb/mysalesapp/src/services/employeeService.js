

import axios from 'axios'

const KEYS = {
    employees: 'employees',
    employeeId: 'employeeId'
}

export function insertEmployee(data) {
    console.log(data)
    //axios.get('http://127.0.0.1:5000/spyneweb/', data)

    let employees = getAllEmployees();
    data['id'] = generateEmployeeId()
    employees.push(data)
    localStorage.setItem(KEYS.employees, JSON.stringify(employees))
}


export function updateEmployee(data) {
    //console.log(data)
    let employees = getAllEmployees();
    let recordIndex = employees.findIndex(x => x.id == data.id);
    employees[recordIndex] = { ...data }
    localStorage.setItem(KEYS.employees, JSON.stringify(employees));

}

export function deleteEmployee(id) {
    let employees = getAllEmployees();
    employees = employees.filter(x => x.id != id)
    localStorage.setItem(KEYS.employees, JSON.stringify(employees));
}

export function generateEmployeeId() {

    if (localStorage.getItem(KEYS.employeeId) == null)
        localStorage.setItem(KEYS.employeeId, '0')
    var id = parseInt(localStorage.getItem(KEYS.employeeId))
    localStorage.setItem(KEYS.employeeId, (++id).toString())
    return id;
}


export function getAllEmployees() {  
    
    // axios.get('http://127.0.0.1:5000/spyneweb/get_all/')

    // .then((res) => {
    //         //alert(res.data)
    //         console.log(typeof(res.data))    //It is object.

    //         // return JSON.parse(res.data);
    //     })
    //     .catch((err) => {
    //         console.log(err)
    //     })

    if (localStorage.getItem(KEYS.employees) == null)
        localStorage.setItem(KEYS.employees, JSON.stringify([]))
    
    console.log(typeof(JSON.parse(localStorage.getItem(KEYS.employees))))
    //alert(JSON.parse(localStorage.getItem(KEYS.employees)))
    //print(res.data)

    return JSON.parse(localStorage.getItem(KEYS.employees));   // it is an object

}
// export function test() {  
//     var arr 
//     axios.get('http://127.0.0.1:5000/spyneweb/get_all/')

//     .then((res) => {
//             //alert(res.data)
//             console.log(typeof(res.data))   
//             arr.push(res.data) //It is object.
//         })
//         .catch((err) => {
//             console.log(err)
//         })

    // if (localStorage.getItem(KEYS.employees) == null)
    //     localStorage.setItem(KEYS.employees, JSON.stringify([]))
    
    // console.log(typeof(JSON.parse(localStorage.getItem(KEYS.employees))))
    //alert(JSON.parse(localStorage.getItem(KEYS.employees)))
    //print(res.data)

    // return JSON.parse(localStorage.getItem(KEYS.employees));   // it is an object
//     return arr
// }

