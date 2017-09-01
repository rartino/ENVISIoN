/*********************************************************************************
 *
 * Copyright (c) 2017 Denise Härnström
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017 Inviwo Foundation
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *********************************************************************************/

#include <modules/crystalvisualization/intvectorpropertywidgetqt.h>
#include <QLineEdit>
#include <QHBoxLayout>

namespace inviwo {

IntVectorPropertyWidgetQt::IntVectorPropertyWidgetQt(IntVectorProperty* property)
    : PropertyWidgetQt(property)
    , property_(property){

    generateWidget();
    updateFromProperty();
}

void IntVectorPropertyWidgetQt::generateWidget() {
    label_ = new EditableLabelQt(this, property_, false);

    //widget layout
    QHBoxLayout* hLayout = new QHBoxLayout();
    setSpacingAndMargins(hLayout);
    hLayout->addWidget(label_);

    lineEdit_ = new QLineEdit();

    QSizePolicy sizePolicy(lineEdit_->sizePolicy());
    sizePolicy.setHorizontalStretch(3);
    sizePolicy.setVerticalPolicy(QSizePolicy::Fixed);
    lineEdit_->setSizePolicy(sizePolicy);

    lineEdit_->setReadOnly(true);
    hLayout->addWidget(lineEdit_);

    setLayout(hLayout);

}

void IntVectorPropertyWidgetQt::updateFromProperty() {
    if(lineEdit_) {
        lineEdit_->clear();
        QString text;
        for (const auto &ind : property_->get()) {
            text.append(QString::number(ind));
            text.append(", ");
        }
        text.chop(2);
        lineEdit_->insert(text);
    }

}

} // namespace
