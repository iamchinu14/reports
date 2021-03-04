
import React, { useState, useEffect } from 'react'
import { Grid, TextField} from '@material-ui/core';
import Controls from "../../components/controls/Controls";
import { useForm, Form } from '../../components/useForm';
import * as employeeService from "../../services/employeeService";


const initialFValues = {
    id: 0,
    fullName: '',
    email: '',
    LeadsAssigned: '0',
    yettopick: '0',
    demoscheduled: '0',
    demodone: '0',
    followup: '0',
    notreachable: '0',
    dead: '0',
    won: '0',
    hireDate: new Date(),
}

export default function EmployeeForm(props) {
    
    const { addOrEdit, recordForEdit } = props
    
    const validate = (fieldValues = values) => {
        let temp = { ...errors }
        if ('fullName' in fieldValues)
            temp.fullName = fieldValues.fullName ? "" : "This field is required."
        if ('email' in fieldValues)
            temp.email = (/$^|.+@.+..+/).test(fieldValues.email) ? "" : "Email is not valid."
        setErrors({
            ...temp
        })

        if (fieldValues == values)
            return Object.values(temp).every(x => x == "")
    }


     const {
        values,
        setValues,
        errors,
        setErrors,
        handleInputChange,
        resetForm
    } = useForm(initialFValues, true, validate);


    const handleSubmit = e => {
        e.preventDefault()
        if (validate()) {
            addOrEdit(values, resetForm);
        }
    }

    useEffect(() => {
        if (recordForEdit != null)
            setValues({
                ...recordForEdit
            })
    }, [recordForEdit])

    return (
        <Form onSubmit={handleSubmit}>

            <Grid container spacing={3}>

                <Grid item xs={6}>

                    <Controls.Input
                        name="fullName"
                        label="Full Name"
                        value={values.fullName}
                        onChange={handleInputChange}
                        error={errors.fullName}
                    />

                  </Grid>

                  <Grid item xs={3}>

                    <TextField                                                     
                        id="filled-number"
                        label="Leads Assigned"
                        name = 'LeadsAssigned'
                        type="number"
                        InputLabelProps={{
                        shrink: true,
                             }}
                        variant="filled"
                        onChange={handleInputChange}
                        />

                    </Grid>

                    <Grid item xs={3}>

                    <TextField                                                     
                        id="filled-number"
                        label="Yet to pick"
                        name = 'yettopick'
                        type="number"
                        InputLabelProps={{
                        shrink: true,
                             }}
                        variant="filled"
                        onChange={handleInputChange}
                    />

                     </Grid>
              

            
                <Grid item xs={6}>

                <Controls.Input
                    label="Email"
                    name="email"
                    value={values.email}
                    onChange={handleInputChange}
                    error={errors.email}
                    />

               
                 </Grid>

                 <Grid item xs={2}>

                 <TextField                                                     
                    id="filled-number"
                    label="Demo Scheduled"
                    name = 'demoscheduled'
                    type="number"
                    InputLabelProps={{
                    shrink: true,
                    }}
                    variant="filled"
                    onChange={handleInputChange}
                    />

                  </Grid>

                  <Grid item xs={2}>

                 <TextField                                                     
                    id="filled-number"
                    label="Demo Done"
                    name = 'demodone'
                    type="number"
                    InputLabelProps={{
                    shrink: true,
                    }}
                    variant="filled"
                    onChange={handleInputChange}
                    />

                  </Grid>


                   <Grid item xs={2}>

                 <TextField                                                     
                    id="filled-number"
                    label="Follow up"
                    name = 'followup'
                    type="number"
                    InputLabelProps={{
                    shrink: true,
                        }}
                    variant="filled"
                    onChange={handleInputChange}
                    />

                  </Grid>

                <Grid item xs={6}>

                <Controls.DatePicker
                    name="hireDate"
                    label="Date"
                    value={values.hireDate}
                    onChange={handleInputChange}
                    />

                </Grid>


                <Grid item xs={2}>

                 <TextField                                                     
                    id="filled-number"
                    label="Not Reachable"
                    name = 'notreachable'
                    type="number"
                    InputLabelProps={{
                    shrink: true,
                             }}
                    variant="filled"
                    onChange={handleInputChange}
                    />

                  </Grid>


                  <Grid item xs={2}>

                 <TextField                                                     
                        id="filled-number"
                        label="Dead"
                        name = 'dead'
                        type="number"
                        InputLabelProps={{
                        shrink: true,
                             }}
                        variant="filled"
                        onChange={handleInputChange}
                    />

                  </Grid>



                  <Grid item xs={2}>

                 <TextField                                                     
                        id="filled-number"
                        label="Won"
                        name = 'won'
                        type="number"
                        InputLabelProps={{
                        shrink: true,
                             }}
                        variant="filled"
                        onChange={handleInputChange}
                    />


                  </Grid>


                  <div>
                        <Controls.Button
                            type="submit"
                            text="Submit" />
                        <Controls.Button
                            text="Reset"
                            color="default"
                            onClick={resetForm} />
                    </div>
        </Grid>
        </Form>
    )
}