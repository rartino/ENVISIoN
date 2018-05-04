#ifndef KDTREE_H
#define KDTREE_H
#include <algorithm>
#include <memory>
#include <exception>
#include <cmath>

template<class T>
class KDData {
public:
    KDData(T value) : value_(value) {}
    virtual ~KDData() = default;

    virtual KDData* getLeft() const = 0;
    virtual KDData* getRight() const = 0;
    virtual bool isLeaf() const = 0;
    virtual size_t getAxis() const = 0;
    T getValue() const {
        return value_;
    }

private:
    T value_;
};

template<class T>
class KDNode : public KDData<T> {
public:
    KDNode(KDData<T>* left, KDData<T>* right, size_t axis,  T value) :
        KDData<T>(value), left_(left), right_(right), axis_(axis) {
    }

    virtual ~KDNode() {
        delete left_;
        delete right_;
    }

    KDData<T>* getLeft() const override {
        return left_;
    }

    KDData<T>* getRight() const override {
        return right_;
    }

    bool isLeaf() const override {
        return false;
    }

    size_t getAxis() const override {
        return axis_;
    }

private:
    KDData<T>* left_;
    KDData<T>* right_;

    size_t axis_;
};

template<class T>
class KDLeaf : public KDData<T> {
public:
    KDLeaf(T value) : KDData<T>(value) {}
    virtual ~KDLeaf() = default;

    KDData<T>* getLeft() const override {
        return nullptr;
    }

    KDData<T>* getRight() const override {
        return nullptr;
    }

    bool isLeaf() const override {
        return true;
    }

    size_t getAxis() const override {
        return 0;
    }
};

// Specialisation for containers and implementation.
template<class T, size_t Dimension>
class KDTree {
public:
    using ElementName = typename T::value_type;
    explicit KDTree(T points) {
        rootNode = constructNode(points, 0);
    }

    ~KDTree() {
        delete rootNode;
    }

    ElementName findNN(const ElementName& point) const {
        float bestDistance = getDistance2(point, rootNode);
        KDData<ElementName>* bestNode = rootNode;
        nnHelper(point, rootNode, bestNode, bestDistance, 0);
        return bestNode->getValue();
    }

private:
    void nnHelper(const ElementName& point, KDData<ElementName>* currentNode,
                  KDData<ElementName>*& bestNode, float& bestDistance, size_t depth) const {
        if (!currentNode) {
            return;
        }

        size_t axis = depth % Dimension;

        float d = getDistance2(point, currentNode);
        if (currentNode->isLeaf()) {
            if (d < bestDistance && !areEqual(point, currentNode->getValue())) {
                bestDistance = d;
                bestNode = currentNode;
            }
        } else {
            KDData<ElementName>* other;
            if (currentNode->getValue()[axis] < point[axis]) {
                nnHelper(point, currentNode->getLeft(), bestNode, bestDistance, depth + 1);
                other = currentNode->getRight();
            } else {
                nnHelper(point, currentNode->getRight(), bestNode, bestDistance, depth + 1);
                other = currentNode->getLeft();
            }

            if (d < bestDistance && !areEqual(point, currentNode->getValue())) {
                bestNode = currentNode;
                bestDistance = d;
            }

            if (other) {
                if ( d >= std::pow(other->getValue()[axis] - point[axis], 2)) {
                    nnHelper(point, other, bestNode, bestDistance, depth + 1);
                }
            }
        }
    }

    float getDistance2(const ElementName& point, KDData<ElementName>* node) const {
        const ElementName& value = node->getValue();
        float d = 0;
        for (size_t dim = 0; dim < Dimension; dim++) {
            d += std::pow(point[dim] - value[dim], 2);
        }

        return d;
    }

    bool areEqual(const ElementName& e1, const ElementName& e2) const {
        for (size_t i = 0; i < Dimension; i++) {
            if (e1[i] != e2[i]) {
                return false;
            }
        }

        return true;
    }

    KDData<ElementName>* constructNode(T& points, size_t depth) {
        KDData<ElementName>* node;
        size_t axis = depth % Dimension;

        if (points.size() == 1) {
            node = new KDLeaf<ElementName>(points[0]);
        } else if (points.size() == 2) {
            sortPoints(points, axis);

            KDLeaf<ElementName>* left = new KDLeaf<ElementName>(points[0]);
            node = new KDNode<ElementName>(left, nullptr, axis, points[1]);
        } else {
            sortPoints(points, axis);

            auto median = points.begin() + points.size() / 2;

            T leftPoints;
            leftPoints.insert(leftPoints.begin(), points.begin(), median);

            T rightPoints;
            rightPoints.insert(rightPoints.begin(), median + 1, points.end());


            node = new KDNode<ElementName>(constructNode(leftPoints, depth + 1),
                                           constructNode(rightPoints, depth + 1),
                                           axis,
                                           *median);
        }


        return node;

    } 

    void sortPoints(T& points, size_t axis) {
            std::sort(points.begin(), points.end(),
            [&](const ElementName& v1, const ElementName& v2)
            {
                return v1[axis] < v2[axis];
            });
    }

    KDData<ElementName>* rootNode;
};

#endif
