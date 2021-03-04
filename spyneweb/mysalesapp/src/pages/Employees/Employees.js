
import React, { useState,useEffect } from 'react'
import EmployeeForm from "./EmployeeForm";
import PageHeader from "../../components/PageHeader";
import PeopleOutlineTwoToneIcon from '@material-ui/icons/PeopleOutlineTwoTone';
import { Paper, makeStyles, TableBody, TableRow, TableCell, Toolbar, InputAdornment } from '@material-ui/core';
import useTable from "../../components/useTable";
import * as employeeService from "../../services/employeeService";
import {getAllEmployees} from '../../services/employeeService';
import Controls from "../../components/controls/Controls";
import { Search } from "@material-ui/icons";
import AddIcon from '@material-ui/icons/Add';
import Popup from "../../components/Popup";
import EditOutlinedIcon from '@material-ui/icons/EditOutlined';
import CloseIcon from '@material-ui/icons/Close';
import Notification from "../../components/Notification";
import ConfirmDialog from "../../components/ConfirmDialog";
import axios from 'axios'

const useStyles = makeStyles(theme => ({
    pageContent: {
        margin: theme.spacing(2),
        padding: theme.spacing(1)
    },
    searchInput: {
        width: '75%'
    },
    newButton: {
        position: 'absolute',
        right: '10px'
    }
}))

const headCells = [
    { id: 'fullName', label: 'Name' },
    { id: 'email', label: 'Email Address' },
    { id: 'hireDate', label: 'Date' },
    { id: 'LeadsAssigned', label: 'LeadsAssigned', disableSorting: true  },  
    { id: 'yettopick', label: 'Yet to pick', disableSorting: true  }, 
    { id: 'demoscheduled', label: 'Demo Scheduled', disableSorting: true  },
    { id: 'demodone', label: 'Demo Done', disableSorting: true  },
    { id: 'followup', label: 'FollowUp', disableSorting: true  },
    { id: 'notreachable', label: 'Not Reachable', disableSorting: true  },
    { id: 'dead', label: 'Dead', disableSorting: true  },
    { id: 'won', label: 'Won', disableSorting: true  },
    { id: 'actions', label: 'Actions', disableSorting: true },
   
]

export default function Employees() {
    const classes = useStyles();
    const [recordForEdit, setRecordForEdit] = useState(null)
    const [records, setRecords] = useState(employeeService.getAllEmployees())
    const [test,setTest] = useState([])
    const [filterFn, setFilterFn] = useState({ fn: items => { return items; } })
    const [openPopup, setOpenPopup] = useState(false)
    const [notify, setNotify] = useState({ isOpen: false, message: '', type: '' })
    const [confirmDialog, setConfirmDialog] = useState({ isOpen: false, title: '', subTitle: '' })
    const [flag_delete, setFlagDelete] = useState(false)
    
    console.log(test)
    const handleSearch = e => {
        let target = e.target;
        setFilterFn({
            fn: items => {
                if (target.value == "")
                    return items;
                else
                    return items.filter(x => x.fullName.toLowerCase().includes(target.value))
            }
        })
    }

    const addOrEdit = (employee, resetForm) => {
        console.log(employee)
        if (employee.id == 0)
            axios.post("/spyneweb/insertion/", employee)
            .then((res) => {
            fetchData()
        })

        else
            axios.post("/spyneweb/updatation/", employee)
            .then((res) => {
            fetchData()
        })

        resetForm()

        setRecordForEdit(null)

        setOpenPopup(false)

        setNotify({
            isOpen: true,
            message: 'Submitted Successfully',
            type: 'success'
        })
    }


    const openInPopup = item => {
        setRecordForEdit(item)
        setOpenPopup(true)
    }

    const onDelete = ids => {
        setConfirmDialog({
            ...confirmDialog,
            isOpen: false
        })

        axios.get(`/spyneweb/deletion/${ids}`)
        .then((res) => {
            fetchData()
        })
       

        setNotify({
            isOpen: true,
            message: 'Deleted Successfully',
            type: 'error'
        })
    }
    useEffect(() => {
    fetchData()

    },[])

    const fetchData = () => {

    axios.get('/spyneweb/get_all/')

    .then((res) => {
            setTest(res.data)//It is object.
        })
        .catch((err) => {
            console.log(err)
        })
    }
    console.log(test)
    const {
        TblContainer,
        TblHead,
        TblPagination,
        recordsAfterPagingAndSorting
    } = useTable(test, headCells, filterFn);
    console.log(test)
    return (
        <>
        
        <PageHeader
                title="Spyne Web"
                subTitle="All Leads"
                icon={<PeopleOutlineTwoToneIcon fontSize="large" />}
            />
            <Paper className={classes.pageContent}>



           
                <Toolbar>
                    <Controls.Input
                        label="Search Employees"
                        className={classes.searchInput}
                        InputProps={{
                            startAdornment: (<InputAdornment position="start">
                                <Search />
                            </InputAdornment>)
                        }}
                        onChange={handleSearch}
                    />


                    <Controls.Button
                        text="Add New"
                        variant="outlined"
                        startIcon={<AddIcon />}
                        className={classes.newButton}
                        onClick={() => { setOpenPopup(true); setRecordForEdit(null); }}
                    />
                </Toolbar>
                <TblContainer>
                    <TblHead />
                    <TableBody>
                        {
                            recordsAfterPagingAndSorting().map(item =>
                                (<TableRow key={item.id}>
                                    <TableCell>{item.fullName}</TableCell>
                                    <TableCell>{item.email}</TableCell>
                                    <TableCell>{item.hireDate}</TableCell>
                                    <TableCell>{item.LeadsAssigned}</TableCell>
                                    <TableCell>{item.yettopick}</TableCell>
                                    <TableCell>{item.demoscheduled}</TableCell>
                                    <TableCell>{item.demodone}</TableCell>
                                    <TableCell>{item.followup}</TableCell>
                                    <TableCell>{item.notreachable}</TableCell>
                                    <TableCell>{item.dead}</TableCell>
                                    <TableCell>{item.won}</TableCell>

                                    <TableCell>
                                        <Controls.ActionButton
                                            color="primary"
                                            onClick={() => { openInPopup(item) }}>
                                            <EditOutlinedIcon fontSize="small" />
                                        </Controls.ActionButton>
                                        <Controls.ActionButton
                                            color="secondary"
                                            onClick={() => {
                                                setConfirmDialog({
                                                    isOpen: true,
                                                    title: 'Are you sure to delete this record?',
                                                    subTitle: "You can't undo this operation",
                                                    onConfirm: () => { onDelete(item.id) }
                                                })
                                            }}>
                                            <CloseIcon fontSize="small" />
                                        </Controls.ActionButton>
                                    </TableCell>

                                    </TableRow>)
                            )
                        }
                    </TableBody>
                </TblContainer>
                <TblPagination />
            </Paper>
            <Popup
                title="New Entry"
                openPopup={openPopup}
                setOpenPopup={setOpenPopup}
            >
                <EmployeeForm
                    recordForEdit={recordForEdit}
                    addOrEdit={addOrEdit} />
            </Popup>
            <Notification
                notify={notify}
                setNotify={setNotify}
            />
            <ConfirmDialog
                confirmDialog={confirmDialog}
                setConfirmDialog={setConfirmDialog}
            />
        </>
    )
}