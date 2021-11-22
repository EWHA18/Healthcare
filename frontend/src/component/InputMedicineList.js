// Medicine list 
// 입력받은 Medicine list를 To do list처럼 나열 해주는 것
import React from 'react';

const InputMedicineList = ({medicines}) => {
    return(
        <div>
            {/*입력받은 medicine list (medicines) 쪼개기*/}
            {medicines.map(m=>(
                <div key={m.id} className="medicine-"> {m.weight}kg |  {m.name}, {m.intake}정</div>
            ))}
        </div>
    )
}

export default InputMedicineList;